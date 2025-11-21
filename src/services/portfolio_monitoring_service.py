"""
포트폴리오 모니터링 서비스 - 백그라운드에서 지속적으로 모니터링
"""
from datetime import datetime
from typing import Any, Dict, List

from config.database import db
from config.logging import get_logger
from src.models.notification import NotificationType
from src.repositories import (
    FinancialGoalRepository,
    InvestmentRecordRepository,
    UserRepository,
)
from src.services.chat_service import ChatService
from src.services.notification_service import NotificationService
from src.services.portfolio_service import PortfolioService

logger = get_logger(__name__)


class PortfolioMonitoringService:
    """포트폴리오 자동 모니터링 서비스"""
    
    def __init__(self):
        self.portfolio_service = PortfolioService()
        self.chat_service = ChatService()
        self.notification_service = NotificationService()
        self.user_repo = UserRepository(db)
        self.goal_repo = FinancialGoalRepository(db)
        self.investment_repo = InvestmentRecordRepository(db)
    
    async def monitor_all_users(self):
        """모든 사용자의 포트폴리오 모니터링"""
        try:
            users = await self.user_repo.get_all()
            logger.info(f"Starting portfolio monitoring for {len(users)} users")
            
            for user in users:
                try:
                    await self.monitor_user_portfolio(user.id)
                except Exception as e:
                    logger.error(f"Error monitoring user {user.id}: {e}", exc_info=True)
            
            logger.info("Portfolio monitoring completed for all users")
        except Exception as e:
            logger.error(f"Error in monitor_all_users: {e}", exc_info=True)
    
    async def monitor_user_portfolio(self, user_id: int) -> Dict[str, Any]:
        """
        특정 사용자 포트폴리오 모니터링 및 자동 조치
        
        Returns:
            모니터링 결과 딕셔너리
        """
        try:
            # 1. 포트폴리오 분석
            portfolio_analysis = await self.portfolio_service.analyze_portfolio(user_id)
            
            # 2. 목표 진행 상황 확인
            goals = await self.goal_repo.get_by_user_id(user_id)
            
            # 3. 리스크 체크
            risk_alerts = await self._check_risk_thresholds(user_id, portfolio_analysis)
            
            # 4. 목표 달성도 체크
            goal_alerts = await self._check_goal_progress(user_id, goals, portfolio_analysis)
            
            # 5. 리밸런싱 필요성 체크
            rebalancing_needed = await self._check_rebalancing(user_id, portfolio_analysis)
            
            # 6. 알림이 필요한 경우 Agent가 자동으로 조치
            if risk_alerts or goal_alerts or rebalancing_needed:
                await self._trigger_agent_action(
                    user_id,
                    risk_alerts,
                    goal_alerts,
                    rebalancing_needed,
                    portfolio_analysis
                )
            
            return {
                "user_id": user_id,
                "risk_alerts": risk_alerts,
                "goal_alerts": goal_alerts,
                "rebalancing_needed": rebalancing_needed
            }
            
        except Exception as e:
            logger.error(f"Error monitoring user {user_id}: {e}", exc_info=True)
            return {
                "user_id": user_id,
                "error": str(e)
            }
    
    async def _check_risk_thresholds(
        self,
        user_id: int,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """리스크 임계값 체크"""
        alerts = []
        
        try:
            # 포트폴리오가 없는 경우 스킵
            if not analysis or analysis.get("total_value", 0) == 0:
                return alerts
            
            # 리스크 분석 데이터 확인
            risk_data = analysis.get("risk", {})
            if not risk_data:
                return alerts
            
            # 최대 낙폭 체크 (예: 20% 이상)
            max_drawdown = risk_data.get("max_drawdown", 0)
            if max_drawdown and abs(max_drawdown) > 20:
                alerts.append({
                    "type": "high_drawdown",
                    "value": max_drawdown,
                    "threshold": 20,
                    "message": f"포트폴리오의 최대 낙폭이 {abs(max_drawdown):.2f}%로 높습니다."
                })
            
            # 변동성 체크 (예: 30% 이상)
            volatility = risk_data.get("volatility", 0)
            if volatility and volatility > 30:
                alerts.append({
                    "type": "high_volatility",
                    "value": volatility,
                    "threshold": 30,
                    "message": f"포트폴리오의 변동성이 {volatility:.2f}%로 높습니다."
                })
            
        except Exception as e:
            logger.warning(f"Error checking risk thresholds: {e}")
        
        return alerts
    
    async def _check_goal_progress(
        self,
        user_id: int,
        goals: List,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """목표 진행 상황 체크"""
        alerts = []
        
        try:
            total_value = analysis.get("total_value", 0) if analysis else 0
            
            for goal in goals:
                if goal.target_amount == 0:
                    continue
                
                progress_ratio = float(total_value) / float(goal.target_amount) if goal.target_amount > 0 else 0
                days_remaining = (goal.target_date - datetime.now().date()).days
                
                # 목표 달성 임박 (90% 이상, 아직 목표일 전)
                if progress_ratio >= 0.9 and days_remaining > 0:
                    alerts.append({
                        "type": "goal_near_completion",
                        "goal_id": goal.id,
                        "goal_type": goal.goal_type,
                        "progress": progress_ratio,
                        "message": f"{goal.goal_type} 목표가 {progress_ratio*100:.1f}% 달성되었습니다!"
                    })
                
                # 목표 달성 지연 위험 (진행률이 예상보다 낮음)
                if days_remaining > 0:
                    total_days = (goal.target_date - goal.created_at.date()).days
                    if total_days > 0:
                        expected_progress = 1 - (days_remaining / total_days)
                        if progress_ratio < expected_progress * 0.8:  # 80% 미만 진행
                            alerts.append({
                                "type": "goal_at_risk",
                                "goal_id": goal.id,
                                "goal_type": goal.goal_type,
                                "progress": progress_ratio,
                                "expected": expected_progress,
                                "message": f"{goal.goal_type} 목표 달성이 지연되고 있습니다. 현재 진행률: {progress_ratio*100:.1f}%"
                            })
        
        except Exception as e:
            logger.warning(f"Error checking goal progress: {e}")
        
        return alerts
    
    async def _check_rebalancing(
        self,
        user_id: int,
        analysis: Dict[str, Any]
    ) -> bool:
        """리밸런싱 필요성 체크"""
        try:
            # 자산 배분 확인
            asset_allocation = analysis.get("asset_allocation", {})
            if not asset_allocation:
                return False
            
            # 목표 배분과 비교 (간단한 체크)
            # 실제로는 사용자의 투자 성향에서 목표 배분을 가져와야 함
            # 여기서는 간단히 균형이 깨졌는지만 확인
            total_allocation = sum(asset_allocation.values())
            if total_allocation == 0:
                return False
            
            # 한 자산 유형이 70% 이상이면 리밸런싱 필요
            for asset_type, percentage in asset_allocation.items():
                if percentage / total_allocation > 0.7:
                    return True
        
        except Exception as e:
            logger.warning(f"Error checking rebalancing: {e}")
        
        return False
    
    async def _trigger_agent_action(
        self,
        user_id: int,
        risk_alerts: List[Dict],
        goal_alerts: List[Dict],
        rebalancing_needed: bool,
        portfolio_analysis: Dict[str, Any]
    ):
        """Agent가 자동으로 조치 취하기"""
        try:
            from src.agents.autonomous_investment_agent import AutonomousInvestmentAgent
            
            agent = AutonomousInvestmentAgent()
            
            # 상황에 맞는 메시지 생성
            action_message = self._build_action_message(
                risk_alerts,
                goal_alerts,
                rebalancing_needed
            )
            
            # Agent가 자동으로 조언 생성
            context = {"user_id": user_id}
            response = ""
            async for chunk in agent.chat(action_message, context=context):
                response += chunk
            
            # 채팅 메시지로 저장
            await self.chat_service.save_message(
                user_id=user_id,
                role="assistant",
                content=f"🔔 자동 모니터링 알림:\n\n{response}",
                project_id=None
            )
            
            # 알림 생성 (이메일 전송)
            notification_type = NotificationType.PORTFOLIO_REVIEW
            if risk_alerts:
                notification_type = NotificationType.RISK_ALERT
            elif goal_alerts:
                if any(a.get("type") == "goal_at_risk" for a in goal_alerts):
                    notification_type = NotificationType.GOAL_AT_RISK
                else:
                    notification_type = NotificationType.GOAL_PROGRESS
            
            await self.notification_service.create_notification(
                user_id=user_id,
                type=notification_type,
                title="포트폴리오 모니터링 결과",
                message=response[:500],  # 처음 500자만
                metadata={
                    "risk_alerts": risk_alerts,
                    "goal_alerts": goal_alerts,
                    "rebalancing_needed": rebalancing_needed
                },
                send_email=True
            )
            
            logger.info(f"Agent action triggered for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error triggering agent action: {e}", exc_info=True)
    
    def _build_action_message(
        self,
        risk_alerts: List[Dict],
        goal_alerts: List[Dict],
        rebalancing_needed: bool
    ) -> str:
        """상황에 맞는 액션 메시지 생성"""
        parts = []
        
        if risk_alerts:
            parts.append("포트폴리오 리스크 경고가 발생했습니다:")
            for alert in risk_alerts:
                parts.append(f"- {alert.get('message', '')}")
        
        if goal_alerts:
            parts.append("\n목표 진행 상황:")
            for alert in goal_alerts:
                parts.append(f"- {alert.get('message', '')}")
        
        if rebalancing_needed:
            parts.append("\n리밸런싱이 필요합니다. 현재 자산 배분이 목표 비중에서 벗어났습니다.")
        
        message = "\n".join(parts)
        return f"다음 상황을 확인했습니다. 적절한 조치를 제안해주세요:\n\n{message}"

