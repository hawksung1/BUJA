"""
목표 추적 서비스
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from config.database import db
from config.logging import get_logger
from src.repositories import FinancialGoalRepository, InvestmentRecordRepository
from src.services.portfolio_service import PortfolioService

logger = get_logger(__name__)


class GoalTrackingService:
    """목표 추적 서비스"""
    
    def __init__(self):
        self.goal_repo = FinancialGoalRepository(db)
        self.portfolio_service = PortfolioService()
        self.investment_repo = InvestmentRecordRepository(db)
    
    async def calculate_goal_progress(
        self,
        user_id: int,
        goal_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        목표 진행률 계산
        
        Args:
            user_id: 사용자 ID
            goal_id: 목표 ID (None이면 모든 목표)
        
        Returns:
            목표 진행률 정보
        """
        try:
            # 포트폴리오 가치 조회
            portfolio_analysis = await self.portfolio_service.analyze_portfolio(user_id)
            total_value = float(portfolio_analysis.get("total_value", 0)) if portfolio_analysis else 0
            
            # 목표 조회
            if goal_id:
                goal = await self.goal_repo.get_by_id(goal_id)
                goals = [goal] if goal and goal.user_id == user_id else []
            else:
                goals = await self.goal_repo.get_by_user_id(user_id)
            
            results = []
            for goal in goals:
                target_amount = float(goal.target_amount)
                current_progress = float(goal.current_progress) if goal.current_progress else 0
                
                # 현재 포트폴리오 가치를 목표 진행률에 반영
                # 목표별로 포트폴리오 가치를 분배하는 로직은 복잡하므로
                # 여기서는 전체 포트폴리오 가치를 사용
                progress_ratio = total_value / target_amount if target_amount > 0 else 0
                days_remaining = (goal.target_date - date.today()).days
                
                # 목표 달성 예상일 계산
                estimated_completion_date = None
                if progress_ratio > 0 and progress_ratio < 1:
                    # 간단한 선형 예측
                    days_elapsed = (date.today() - goal.created_at.date()).days
                    if days_elapsed > 0:
                        progress_per_day = progress_ratio / days_elapsed
                        if progress_per_day > 0:
                            days_to_complete = (1 - progress_ratio) / progress_per_day
                            estimated_completion_date = date.today() + timedelta(days=int(days_to_complete))
                
                results.append({
                    "goal_id": goal.id,
                    "goal_type": goal.goal_type,
                    "target_amount": target_amount,
                    "current_value": total_value,
                    "current_progress": current_progress,
                    "progress_ratio": min(progress_ratio, 1.0),  # 100% 초과 방지
                    "days_remaining": days_remaining,
                    "estimated_completion_date": estimated_completion_date.isoformat() if estimated_completion_date else None,
                    "is_completed": progress_ratio >= 1.0
                })
            
            return {
                "user_id": user_id,
                "total_portfolio_value": total_value,
                "goals": results
            }
            
        except Exception as e:
            logger.error(f"Error calculating goal progress: {e}", exc_info=True)
            return {
                "user_id": user_id,
                "error": str(e)
            }
    
    async def predict_goal_achievement(
        self,
        user_id: int,
        goal_id: int
    ) -> Dict[str, Any]:
        """
        목표 달성 예측
        
        Args:
            user_id: 사용자 ID
            goal_id: 목표 ID
        
        Returns:
            목표 달성 예측 정보
        """
        try:
            goal = await self.goal_repo.get_by_id(goal_id)
            if not goal or goal.user_id != user_id:
                return {"error": "Goal not found"}
            
            # 포트폴리오 분석
            portfolio_analysis = await self.portfolio_service.analyze_portfolio(user_id)
            current_value = float(portfolio_analysis.get("total_value", 0)) if portfolio_analysis else 0
            
            target_amount = float(goal.target_amount)
            days_remaining = (goal.target_date - date.today()).days
            
            # 필요한 추가 금액
            needed_amount = max(0, target_amount - current_value)
            
            # 예상 수익률 (간단히 5% 가정, 실제로는 포트폴리오 분석에서 가져와야 함)
            expected_return = 0.05
            
            # 목표 달성 가능성 계산
            if days_remaining <= 0:
                achievement_probability = 1.0 if current_value >= target_amount else 0.0
            else:
                # 현재 진행률
                current_progress = current_value / target_amount if target_amount > 0 else 0
                
                # 예상 진행률 (현재 진행률 + 예상 수익)
                expected_progress = min(1.0, current_progress * (1 + expected_return))
                
                # 목표 달성 가능성 (간단한 추정)
                achievement_probability = min(1.0, expected_progress * (365 / max(days_remaining, 1)))
            
            return {
                "goal_id": goal_id,
                "current_value": current_value,
                "target_amount": target_amount,
                "needed_amount": needed_amount,
                "days_remaining": days_remaining,
                "achievement_probability": achievement_probability,
                "is_on_track": achievement_probability >= 0.7
            }
            
        except Exception as e:
            logger.error(f"Error predicting goal achievement: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def assess_goal_risk(
        self,
        user_id: int,
        goal_id: int
    ) -> Dict[str, Any]:
        """
        목표 달성 위험도 평가
        
        Args:
            user_id: 사용자 ID
            goal_id: 목표 ID
        
        Returns:
            목표 달성 위험도 정보
        """
        try:
            goal = await self.goal_repo.get_by_id(goal_id)
            if not goal or goal.user_id != user_id:
                return {"error": "Goal not found"}
            
            # 진행률 계산
            progress_info = await self.calculate_goal_progress(user_id, goal_id)
            goal_data = progress_info.get("goals", [])
            if not goal_data:
                return {"error": "Goal data not found"}
            
            goal_data = goal_data[0]
            progress_ratio = goal_data.get("progress_ratio", 0)
            days_remaining = goal_data.get("days_remaining", 0)
            
            # 위험도 계산
            total_days = (goal.target_date - goal.created_at.date()).days
            if total_days <= 0:
                risk_score = 1.0  # 매우 위험
            else:
                expected_progress = 1 - (days_remaining / total_days)
                progress_gap = expected_progress - progress_ratio
                
                # 위험 점수 (0.0 = 안전, 1.0 = 매우 위험)
                if progress_gap <= 0:
                    risk_score = 0.0  # 목표보다 앞서 있음
                elif progress_gap < 0.1:
                    risk_score = 0.3  # 약간 지연
                elif progress_gap < 0.2:
                    risk_score = 0.6  # 중간 지연
                else:
                    risk_score = 1.0  # 심각한 지연
            
            risk_level = "low" if risk_score < 0.3 else "medium" if risk_score < 0.7 else "high"
            
            return {
                "goal_id": goal_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "progress_ratio": progress_ratio,
                "expected_progress": expected_progress if total_days > 0 else 0,
                "progress_gap": progress_gap,
                "days_remaining": days_remaining,
                "recommendation": self._get_risk_recommendation(risk_level, progress_gap)
            }
            
        except Exception as e:
            logger.error(f"Error assessing goal risk: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _get_risk_recommendation(self, risk_level: str, progress_gap: float) -> str:
        """위험도에 따른 추천 메시지"""
        if risk_level == "low":
            return "목표 달성이 순조롭게 진행되고 있습니다."
        elif risk_level == "medium":
            return "목표 달성을 위해 투자 전략을 재검토하는 것을 권장합니다."
        else:
            return "목표 달성이 지연되고 있습니다. 즉시 투자 전략을 조정해야 합니다."

