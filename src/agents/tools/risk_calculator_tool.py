"""
리스크 계산 Tool
"""
from typing import Any, Dict, Optional

from config.logging import get_logger
from src.agents.tools.base_tool import BaseTool
from src.analyzers.risk_analyzer import RiskAnalyzer

logger = get_logger(__name__)


class RiskCalculatorTool(BaseTool):
    """리스크 계산 Tool"""

    def __init__(self):
        super().__init__(
            name="calculate_risk",
            description="포트폴리오의 리스크를 계산합니다. VaR, Sharpe Ratio, 최대 낙폭 등을 계산합니다."
        )
        self.risk_analyzer = RiskAnalyzer()

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "portfolio_data": {
                    "type": "object",
                    "description": "포트폴리오 데이터 (자산 유형별 비중)"
                },
                "risk_metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "계산할 리스크 지표 (var, sharpe, max_drawdown 등)",
                    "default": ["var", "sharpe"]
                }
            },
            "required": ["portfolio_data"]
        }

    async def execute(self, portfolio_data: Dict[str, Any], risk_metrics: Optional[list] = None, **kwargs) -> Dict[str, Any]:
        """
        리스크 계산 실행
        
        Args:
            portfolio_data: 포트폴리오 데이터
            risk_metrics: 계산할 리스크 지표 목록
        
        Returns:
            리스크 계산 결과
        """
        try:
            if risk_metrics is None:
                risk_metrics = ["var", "sharpe"]

            result = await self.risk_analyzer.calculate_risk(portfolio_data, risk_metrics)

            logger.info("Risk calculation completed")
            return {
                "status": "success",
                "risk_metrics": result
            }

        except Exception as e:
            logger.error(f"Risk calculation error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "risk_metrics": None
            }

