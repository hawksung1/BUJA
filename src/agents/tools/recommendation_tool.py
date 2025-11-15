"""
투자 추천 Tool
"""
from typing import Dict, Any, Optional
from src.agents.tools.base_tool import BaseTool
from src.services.recommendation_service import RecommendationService
from config.logging import get_logger

logger = get_logger(__name__)


class RecommendationTool(BaseTool):
    """투자 추천 Tool"""
    
    def __init__(self):
        super().__init__(
            name="get_recommendation",
            description="사용자의 투자 성향과 재무 상황을 기반으로 맞춤형 투자 추천을 생성합니다."
        )
        self.recommendation_service = RecommendationService()
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "사용자 ID"
                },
                "goal_type": {
                    "type": "string",
                    "description": "목표 유형 (RETIREMENT, HOUSE, EDUCATION 등)",
                    "enum": ["RETIREMENT", "HOUSE", "EDUCATION", "TRAVEL", "EMERGENCY", "OTHER"]
                },
                "include_rationale": {
                    "type": "boolean",
                    "description": "추천 근거 포함 여부",
                    "default": True
                }
            },
            "required": ["user_id"]
        }
    
    async def execute(self, user_id: int, goal_type: Optional[str] = None, include_rationale: bool = True, **kwargs) -> Dict[str, Any]:
        """
        투자 추천 생성
        
        Args:
            user_id: 사용자 ID
            goal_type: 목표 유형 (선택사항)
            include_rationale: 추천 근거 포함 여부
        
        Returns:
            추천 결과
        """
        try:
            recommendation = await self.recommendation_service.generate_recommendation(
                user_id=user_id,
                goal_type=goal_type,
                include_rationale=include_rationale
            )
            
            logger.info(f"Recommendation generated for user {user_id}")
            return {
                "status": "success",
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "recommendation": None
            }

