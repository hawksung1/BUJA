"""
MCP (Model Context Protocol) Tool
"""
from typing import Dict, Any, Optional
from src.agents.tools.base_tool import BaseTool
from config.logging import get_logger
import httpx
import json

logger = get_logger(__name__)


class MCPTool(BaseTool):
    """MCP Tool 구현"""
    
    def __init__(
        self,
        name: str,
        description: str,
        mcp_server_url: str,
        mcp_endpoint: str,
        parameters_schema: Dict[str, Any],
        api_key: Optional[str] = None
    ):
        """
        MCPTool 초기화
        
        Args:
            name: Tool 이름
            description: Tool 설명
            mcp_server_url: MCP 서버 URL
            mcp_endpoint: MCP 엔드포인트 경로
            parameters_schema: 파라미터 스키마 (JSON Schema)
            api_key: API 키 (선택사항)
        """
        super().__init__(name, description)
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.mcp_endpoint = mcp_endpoint.lstrip('/')
        self.parameters_schema = parameters_schema
        self.api_key = api_key
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """파라미터 스키마 반환"""
        return self.parameters_schema
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        MCP Tool 실행
        
        Args:
            **kwargs: Tool 실행에 필요한 파라미터
        
        Returns:
            실행 결과
        """
        try:
            url = f"{self.mcp_server_url}/{self.mcp_endpoint}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=kwargs,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"MCP Tool {self.name} executed successfully")
                return {
                    "status": "success",
                    "data": result
                }
                
        except httpx.HTTPError as e:
            logger.error(f"MCP Tool {self.name} HTTP error: {e}")
            return {
                "status": "error",
                "message": f"HTTP error: {str(e)}",
                "data": None
            }
        except Exception as e:
            logger.error(f"MCP Tool {self.name} execution error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Tool을 딕셔너리로 변환 (저장용)"""
        return {
            "name": self.name,
            "description": self.description,
            "mcp_server_url": self.mcp_server_url,
            "mcp_endpoint": self.mcp_endpoint,
            "parameters_schema": self.parameters_schema,
            "api_key": self.api_key  # 보안상 실제 저장 시 암호화 필요
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPTool":
        """딕셔너리에서 Tool 생성"""
        return cls(
            name=data["name"],
            description=data["description"],
            mcp_server_url=data["mcp_server_url"],
            mcp_endpoint=data["mcp_endpoint"],
            parameters_schema=data["parameters_schema"],
            api_key=data.get("api_key")
        )

