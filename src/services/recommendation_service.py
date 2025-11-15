"""
추천 서비스
"""
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from config.database import Database, db
from src.repositories import (
    AssetRecommendationRepository,
    InvestmentPreferenceRepository,
    FinancialSituationRepository,
)
from src.models import AssetRecommendation
from src.analyzers.asset_allocator import AssetAllocator
from src.services.user_service import UserService
from src.exceptions import UserNotFoundError, ValidationError
from config.logging import get_logger

logger = get_logger(__name__)


class RecommendationService:
    """추천 서비스"""
    
    def __init__(self, database: Optional[Database] = None):
        """
        RecommendationService 초기화
        
        Args:
            database: Database 인스턴스 (기본값: 전역 db 인스턴스)
        """
        self.db = database or db
        self.recommendation_repo = AssetRecommendationRepository(self.db)
        self.preference_repo = InvestmentPreferenceRepository(self.db)
        self.financial_repo = FinancialSituationRepository(self.db)
        self.allocator = AssetAllocator()
        self._agent = None  # Lazy loading to avoid circular import
        self.user_service = UserService(self.db)
    
    @property
    def agent(self):
        """Lazy load InvestmentAgent to avoid circular import"""
        if self._agent is None:
            from src.agents.investment_agent import InvestmentAgent
            self._agent = InvestmentAgent()
        return self._agent
    
    async def generate_initial_recommendation(
        self,
        user_id: int
    ) -> AssetRecommendation:
        """
        최초 자산 구성 추천 생성
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            AssetRecommendation 객체
        """
        # 사용자 존재 확인
        await self.user_service.get_user(user_id)
        
        # 투자 성향 조회
        preference = await self.preference_repo.get_by_user_id(user_id)
        if not preference:
            raise ValidationError("투자 성향이 설정되지 않았습니다.")
        
        # 재무 상황 조회
        financial = await self.financial_repo.get_by_user_id(user_id)
        if not financial or not financial.total_assets:
            raise ValidationError("재무 상황이 설정되지 않았습니다.")
        
        # 자산 배분 계산 (글로벌 포트폴리오 포함)
        allocation_result = self.allocator.calculate_initial_allocation(
            risk_tolerance=preference.risk_tolerance,
            initial_amount=financial.total_assets,
            preferred_types=preference.preferred_asset_types,
            preferred_regions=preference.preferred_regions,
            home_country=preference.home_country,
            currency_hedge_preference=preference.currency_hedge_preference
        )
        
        # Agent를 통한 추천 근거 생성
        context = {
            "investment_preference": {
                "risk_tolerance": preference.risk_tolerance,
                "target_return": float(preference.target_return) if preference.target_return else None,
            },
            "financial_situation": {
                "total_assets": float(financial.total_assets),
            }
        }
        
        reasoning_prompt = (
            f"다음 자산 배분을 추천합니다: {allocation_result['allocation_percentages']}. "
            f"이 추천의 근거를 설명해주세요."
        )
        reasoning = await self.agent.chat(reasoning_prompt, context=context)
        
        # 추천 저장
        async with self.db.session() as session:
            recommendation = AssetRecommendation(
                user_id=user_id,
                recommendation_type="INITIAL",
                target_allocation=allocation_result["allocation_percentages"],
                reasoning=reasoning,
                risk_assessment=f"위험 수준: {allocation_result['risk_level']}",
                expected_return=preference.target_return,
                confidence_score=Decimal("0.8"),  # 기본 신뢰도
                expires_at=datetime.now() + timedelta(days=30)  # 30일 후 만료
            )
            recommendation = await self.recommendation_repo.create(recommendation, session=session)
            await session.commit()
            await session.refresh(recommendation)
            
            logger.info(f"Initial recommendation generated: user_id={user_id}")
            return recommendation
    
    async def get_latest_recommendation(
        self,
        user_id: int,
        recommendation_type: Optional[str] = None
    ) -> Optional[AssetRecommendation]:
        """
        최신 추천 조회
        
        Args:
            user_id: 사용자 ID
            recommendation_type: 추천 타입 (선택사항)
        
        Returns:
            AssetRecommendation 또는 None
        """
        return await self.recommendation_repo.get_latest(
            user_id=user_id,
            recommendation_type=recommendation_type
        )
    
    async def explain_recommendation(
        self,
        recommendation_id: int
    ) -> str:
        """
        추천 근거 설명 생성 (Agent 활용)
        
        Args:
            recommendation_id: 추천 ID
        
        Returns:
            설명 텍스트
        """
        recommendation = await self.recommendation_repo.get_by_id(recommendation_id)
        if not recommendation:
            raise ValidationError("Recommendation not found.")
        
        if recommendation.reasoning:
            return recommendation.reasoning
        
        # Agent를 통한 설명 생성
        prompt = (
            f"다음 자산 배분 추천에 대해 자세히 설명해주세요: "
            f"{recommendation.target_allocation}"
        )
        
        context = {
            "investment_preference": {
                "risk_tolerance": "N/A",
            }
        }
        
        explanation = await self.agent.chat(prompt, context=context)
        
        # 설명 저장
        async with self.db.session() as session:
            recommendation.reasoning = explanation
            await self.recommendation_repo.update(recommendation, session=session)
            await session.commit()
        
        return explanation
    
    async def generate_recommendation(
        self,
        user_id: int,
        goal_type: Optional[str] = None,
        include_rationale: bool = True
    ) -> Dict[str, Any]:
        """
        투자 추천 생성
        
        Args:
            user_id: 사용자 ID
            goal_type: 목표 유형 (선택사항)
            include_rationale: 추천 근거 포함 여부
        
        Returns:
            추천 결과 딕셔너리
        """
        try:
            # 최신 추천 조회 또는 새로 생성
            recommendation = await self.get_latest_recommendation(user_id)
            
            if not recommendation:
                # 새 추천 생성
                recommendation = await self.generate_initial_recommendation(user_id)
            
            result = {
                "recommendation_type": recommendation.recommendation_type,
                "target_allocation": recommendation.target_allocation,
                "expected_return": float(recommendation.expected_return) if recommendation.expected_return else None,
                "risk_assessment": recommendation.risk_assessment,
                "confidence_score": float(recommendation.confidence_score) if recommendation.confidence_score else None,
            }
            
            if include_rationale and recommendation.reasoning:
                result["rationale"] = recommendation.reasoning
            elif include_rationale:
                # 근거 생성
                result["rationale"] = await self.explain_recommendation(recommendation.id)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}", exc_info=True)
            raise

