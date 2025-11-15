"""
투자 성향 관리 서비스
"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
from config.database import Database, db
from src.repositories import InvestmentPreferenceRepository
from src.models import InvestmentPreference
from src.services.user_service import UserService
from src.exceptions import UserNotFoundError, ValidationError
from config.logging import get_logger

logger = get_logger(__name__)


class InvestmentPreferenceService:
    """투자 성향 관리 서비스"""
    
    def __init__(self, database: Optional[Database] = None):
        """
        InvestmentPreferenceService 초기화
        
        Args:
            database: Database 인스턴스 (기본값: 전역 db 인스턴스)
        """
        self.db = database or db
        self.preference_repo = InvestmentPreferenceRepository(self.db)
        self.user_service = UserService(self.db)
    
    async def calculate_risk_tolerance_from_survey(
        self,
        survey_answers: Dict[str, Any]
    ) -> int:
        """
        설문조사 답변으로부터 위험 감수 성향 계산 (1-10)
        
        Args:
            survey_answers: 설문조사 답변 딕셔너리
                - investment_experience: 투자 경험 (BEGINNER, INTERMEDIATE, ADVANCED)
                - investment_period: 투자 기간 (SHORT, MEDIUM, LONG)
                - loss_tolerance: 손실 감내 능력 (1-5)
                - return_expectation: 수익률 기대치 (1-5)
                - volatility_comfort: 변동성 감내 능력 (1-5)
        
        Returns:
            위험 감수 성향 (1-10)
        """
        score = 5  # 기본값 (중립)
        
        # 투자 경험
        experience_scores = {
            "BEGINNER": 2,
            "INTERMEDIATE": 5,
            "ADVANCED": 8
        }
        if "investment_experience" in survey_answers:
            score += experience_scores.get(survey_answers["investment_experience"], 0) - 5
        
        # 투자 기간
        period_scores = {
            "SHORT": 3,
            "MEDIUM": 5,
            "LONG": 7
        }
        if "investment_period" in survey_answers:
            score += period_scores.get(survey_answers["investment_period"], 0) - 5
        
        # 손실 감내 능력 (1-5 -> 0-4 점수)
        if "loss_tolerance" in survey_answers:
            loss_score = survey_answers["loss_tolerance"] - 3  # -2 ~ 2
            score += loss_score
        
        # 수익률 기대치 (1-5 -> 0-4 점수)
        if "return_expectation" in survey_answers:
            return_score = survey_answers["return_expectation"] - 3  # -2 ~ 2
            score += return_score
        
        # 변동성 감내 능력 (1-5 -> 0-4 점수)
        if "volatility_comfort" in survey_answers:
            volatility_score = survey_answers["volatility_comfort"] - 3  # -2 ~ 2
            score += volatility_score
        
        # 1-10 범위로 제한
        score = max(1, min(10, score))
        
        return int(score)
    
    async def create_preference_from_survey(
        self,
        user_id: int,
        survey_answers: Dict[str, Any]
    ) -> InvestmentPreference:
        """
        설문조사 결과로부터 투자 성향 생성
        
        Args:
            user_id: 사용자 ID
            survey_answers: 설문조사 답변
        
        Returns:
            생성된 InvestmentPreference 객체
        """
        # 사용자 존재 확인
        await self.user_service.get_user(user_id)
        
        # 위험 감수 성향 계산
        risk_tolerance = await self.calculate_risk_tolerance_from_survey(survey_answers)
        
        # 투자 성향 데이터 구성
        preference_data = {
            "risk_tolerance": risk_tolerance,
            "investment_period": survey_answers.get("investment_period"),
            "investment_experience": survey_answers.get("investment_experience"),
            "max_loss_tolerance": survey_answers.get("max_loss_tolerance"),
        }
        
        # 목표 수익률 설정 (위험 감수 성향 기반)
        if risk_tolerance <= 3:
            target_return = Decimal("5.0")  # 보수적
        elif risk_tolerance <= 6:
            target_return = Decimal("8.0")  # 중립
        else:
            target_return = Decimal("12.0")  # 공격적
        
        preference_data["target_return"] = target_return
        
        # 선호 자산 유형 설정
        if risk_tolerance <= 3:
            preferred_types = ["BOND", "CASH", "FUND"]
        elif risk_tolerance <= 6:
            preferred_types = ["STOCK", "BOND", "FUND"]
        else:
            preferred_types = ["STOCK", "CRYPTO", "FUND"]
        
        preference_data["preferred_asset_types"] = preferred_types
        
        # 투자 성향 생성
        return await self.user_service.update_investment_preference(
            user_id=user_id,
            preference_data=preference_data
        )
    
    async def get_preference(
        self,
        user_id: int
    ) -> Optional[InvestmentPreference]:
        """
        사용자의 투자 성향 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            InvestmentPreference 또는 None
        """
        return await self.preference_repo.get_by_user_id(user_id)
    
    async def update_preference(
        self,
        user_id: int,
        preference_data: Dict[str, Any]
    ) -> InvestmentPreference:
        """
        투자 성향 업데이트 또는 생성
        
        Args:
            user_id: 사용자 ID
            preference_data: 투자 성향 데이터
            
        Returns:
            업데이트된 InvestmentPreference 객체
        """
        # 사용자 존재 확인
        await self.user_service.get_user(user_id)
        
        # 기존 투자 성향 조회
        existing_preference = await self.preference_repo.get_by_user_id(user_id)
        
        if existing_preference:
            # 업데이트
            for key, value in preference_data.items():
                if hasattr(existing_preference, key):
                    setattr(existing_preference, key, value)
            
            async with self.db.session() as session:
                session.add(existing_preference)
                await session.commit()
                await session.refresh(existing_preference)
                return existing_preference
        else:
            # 새로 생성
            return await self.user_service.update_investment_preference(
                user_id=user_id,
                preference_data=preference_data
            )
    
    async def generate_preference_report(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        투자 성향 분석 리포트 생성
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            분석 리포트 딕셔너리
        """
        preference = await self.preference_repo.get_by_user_id(user_id)
        if not preference:
            raise ValidationError("투자 성향이 설정되지 않았습니다.")
        
        risk_tolerance = preference.risk_tolerance
        
        # 위험 수준 분류
        if risk_tolerance <= 3:
            risk_level = "보수적"
            risk_description = "안정적인 투자를 선호하며, 손실 가능성을 최소화하려는 성향입니다."
        elif risk_tolerance <= 6:
            risk_level = "중립"
            risk_description = "적절한 수익과 리스크의 균형을 추구하는 성향입니다."
        else:
            risk_level = "공격적"
            risk_description = "높은 수익을 추구하며, 변동성을 감수할 수 있는 성향입니다."
        
        # 추천 자산 배분
        if risk_tolerance <= 3:
            recommended_allocation = {
                "주식": 30,
                "채권": 50,
                "현금": 15,
                "기타": 5
            }
        elif risk_tolerance <= 6:
            recommended_allocation = {
                "주식": 60,
                "채권": 30,
                "현금": 5,
                "기타": 5
            }
        else:
            recommended_allocation = {
                "주식": 70,
                "채권": 15,
                "현금": 5,
                "기타": 10
            }
        
        report = {
            "risk_tolerance": risk_tolerance,
            "risk_level": risk_level,
            "risk_description": risk_description,
            "target_return": float(preference.target_return) if preference.target_return else None,
            "investment_period": preference.investment_period,
            "investment_experience": preference.investment_experience,
            "preferred_asset_types": preference.preferred_asset_types or [],
            "max_loss_tolerance": float(preference.max_loss_tolerance) if preference.max_loss_tolerance else None,
            "recommended_allocation": recommended_allocation,
            "updated_at": preference.updated_at.isoformat() if preference.updated_at else None,
        }
        
        logger.info(f"Preference report generated: user_id={user_id}")
        return report

