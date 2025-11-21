"""
자율적 투자 Agent - 능동적으로 모니터링하고 조치
"""
from typing import Any, AsyncGenerator, Dict, Optional

from config.logging import get_logger
from src.agents.investment_agent import InvestmentAgent

logger = get_logger(__name__)


class AutonomousInvestmentAgent(InvestmentAgent):
    """자율적 투자 Agent - 능동적으로 모니터링하고 조치"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_goals: Dict[int, Dict[str, Any]] = {}  # 사용자별 활성 목표
    
    async def monitor_and_act(self, user_id: int) -> Optional[str]:
        """
        능동적으로 모니터링하고 필요한 조치 취하기
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            수행한 액션 설명 (없으면 None)
        """
        from src.services.portfolio_monitoring_service import PortfolioMonitoringService
        
        monitoring = PortfolioMonitoringService()
        
        # 모니터링 실행
        result = await monitoring.monitor_user_portfolio(user_id)
        
        if result.get("risk_alerts") or result.get("goal_alerts") or result.get("rebalancing_needed"):
            return "모니터링 결과를 바탕으로 조치를 취했습니다."
        
        return None
    
    async def create_action_plan(
        self,
        user_id: int,
        situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        상황 분석 및 액션 플랜 수립
        
        Args:
            user_id: 사용자 ID
            situation: 현재 상황 정보
        
        Returns:
            액션 플랜 딕셔너리
        """
        context = {"user_id": user_id}
        
        planning_prompt = f"""
        다음 정보를 바탕으로 사용자의 재무 목표 달성을 위한 구체적인 액션 플랜을 수립해주세요:
        
        현재 상황:
        {situation}
        
        다음을 포함한 액션 플랜을 제시해주세요:
        1. 즉시 조치가 필요한 사항
        2. 단기 계획 (1-3개월)
        3. 중기 계획 (3-6개월)
        4. 장기 계획 (6개월 이상)
        
        각 액션은 구체적이고 실행 가능해야 합니다.
        """
        
        # Agent가 계획 수립
        plan_response = ""
        async for chunk in self.chat(planning_prompt, context=context):
            plan_response += chunk
        
        # 계획을 구조화된 형태로 파싱
        return {
            "plan": plan_response,
            "actions": self._parse_actions(plan_response)
        }
    
    def _parse_actions(self, plan_text: str) -> list:
        """계획 텍스트에서 액션 추출 (간단한 파싱)"""
        # 실제로는 더 정교한 파싱 필요
        # 또는 LLM에게 구조화된 JSON으로 응답 요청
        actions = []
        # TODO: LLM에게 구조화된 JSON으로 응답 요청
        return actions
    
    async def generate_proactive_advice(
        self,
        user_id: int,
        alert_type: str,
        alert_data: Dict[str, Any]
    ) -> str:
        """
        능동적 조언 생성
        
        Args:
            user_id: 사용자 ID
            alert_type: 알림 유형
            alert_data: 알림 데이터
        
        Returns:
            조언 메시지
        """
        context = {"user_id": user_id}
        
        advice_prompt = f"""
        다음 상황에 대해 사용자에게 조언을 제공해주세요:
        
        알림 유형: {alert_type}
        상황: {alert_data}
        
        구체적이고 실행 가능한 조언을 제공해주세요.
        """
        
        response = ""
        async for chunk in self.chat(advice_prompt, context=context):
            response += chunk
        
        return response

