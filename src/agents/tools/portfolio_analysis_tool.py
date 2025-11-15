"""
포트폴리오 분석 Tool
"""
from typing import Dict, Any
from src.agents.tools.base_tool import BaseTool
from src.services.portfolio_service import PortfolioService
from src.repositories import InvestmentRecordRepository
from config.database import db
from config.logging import get_logger

logger = get_logger(__name__)


class PortfolioAnalysisTool(BaseTool):
    """포트폴리오 분석 Tool"""
    
    def __init__(self):
        super().__init__(
            name="analyze_portfolio",
            description="사용자의 현재 포트폴리오를 분석합니다. 자산 배분, 수익률, 리스크 등을 분석하여 반환합니다."
        )
        self.portfolio_service = PortfolioService()
        self.investment_repo = InvestmentRecordRepository(db)
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "사용자 ID"
                },
                "include_risk_analysis": {
                    "type": "boolean",
                    "description": "리스크 분석 포함 여부",
                    "default": True
                }
            },
            "required": ["user_id"]
        }
    
    async def execute(self, user_id: int, include_risk_analysis: bool = True, **kwargs) -> Dict[str, Any]:
        """
        포트폴리오 분석 실행
        
        Args:
            user_id: 사용자 ID
            include_risk_analysis: 리스크 분석 포함 여부
        
        Returns:
            분석 결과
        """
        try:
            # 투자 기록 조회
            records = await self.investment_repo.get_by_user_id(user_id)
            
            if not records:
                return {
                    "status": "no_portfolio",
                    "message": "포트폴리오가 없습니다.",
                    "analysis": None
                }
            
            # 포트폴리오 분석
            analysis = await self.portfolio_service.analyze_portfolio(user_id)
            
            result = {
                "status": "success",
                "analysis": {
                    "total_value": analysis.get("total_value", 0),
                    "asset_allocation": analysis.get("asset_allocation", {}),
                    "performance": analysis.get("performance", {}),
                }
            }
            
            if include_risk_analysis:
                result["analysis"]["risk"] = analysis.get("risk", {})
            
            logger.info(f"Portfolio analysis completed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Portfolio analysis error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "analysis": None
            }

