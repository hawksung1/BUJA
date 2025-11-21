"""
MCP Tool 관리 서비스
"""
import json
from pathlib import Path
from typing import List, Optional

from config.logging import get_logger
from src.agents.tools.mcp_tool import MCPTool

logger = get_logger(__name__)


class MCPToolService:
    """MCP Tool 관리 서비스"""

    def __init__(self):
        """MCPToolService 초기화"""
        # 사용자별 Tool 설정 저장 경로
        self.tools_dir = Path("data/mcp_tools")
        self.tools_dir.mkdir(parents=True, exist_ok=True)

    def get_user_tools_file(self, user_id: int) -> Path:
        """
        사용자별 Tool 설정 파일 경로 반환
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            파일 경로
        """
        return self.tools_dir / f"user_{user_id}_tools.json"

    def save_user_tools(self, user_id: int, tools: List[MCPTool]) -> None:
        """
        사용자 Tool 목록 저장
        
        Args:
            user_id: 사용자 ID
            tools: Tool 목록
        """
        try:
            tools_data = [tool.to_dict() for tool in tools]
            tools_file = self.get_user_tools_file(user_id)

            with open(tools_file, 'w', encoding='utf-8') as f:
                json.dump(tools_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(tools)} MCP tools for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save user tools: {e}", exc_info=True)
            raise

    def load_user_tools(self, user_id: int) -> List[MCPTool]:
        """
        사용자 Tool 목록 로드
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            Tool 목록
        """
        try:
            tools_file = self.get_user_tools_file(user_id)

            if not tools_file.exists():
                return []

            with open(tools_file, 'r', encoding='utf-8') as f:
                tools_data = json.load(f)

            tools = [MCPTool.from_dict(tool_data) for tool_data in tools_data]
            logger.info(f"Loaded {len(tools)} MCP tools for user {user_id}")
            return tools
        except Exception as e:
            logger.error(f"Failed to load user tools: {e}", exc_info=True)
            return []

    def add_user_tool(self, user_id: int, tool: MCPTool) -> None:
        """
        사용자 Tool 추가
        
        Args:
            user_id: 사용자 ID
            tool: 추가할 Tool
        """
        tools = self.load_user_tools(user_id)

        # 중복 체크
        if any(t.name == tool.name for t in tools):
            raise ValueError(f"Tool with name '{tool.name}' already exists")

        tools.append(tool)
        self.save_user_tools(user_id, tools)
        logger.info(f"Added MCP tool '{tool.name}' for user {user_id}")

    def remove_user_tool(self, user_id: int, tool_name: str) -> None:
        """
        사용자 Tool 제거
        
        Args:
            user_id: 사용자 ID
            tool_name: 제거할 Tool 이름
        """
        tools = self.load_user_tools(user_id)
        tools = [t for t in tools if t.name != tool_name]
        self.save_user_tools(user_id, tools)
        logger.info(f"Removed MCP tool '{tool_name}' for user {user_id}")

    def update_user_tool(self, user_id: int, tool_name: str, updated_tool: MCPTool) -> None:
        """
        사용자 Tool 업데이트
        
        Args:
            user_id: 사용자 ID
            tool_name: 업데이트할 Tool 이름
            updated_tool: 업데이트된 Tool
        """
        tools = self.load_user_tools(user_id)

        for i, tool in enumerate(tools):
            if tool.name == tool_name:
                tools[i] = updated_tool
                self.save_user_tools(user_id, tools)
                logger.info(f"Updated MCP tool '{tool_name}' for user {user_id}")
                return

        raise ValueError(f"Tool with name '{tool_name}' not found")

    def get_user_tool(self, user_id: int, tool_name: str) -> Optional[MCPTool]:
        """
        사용자 Tool 조회
        
        Args:
            user_id: 사용자 ID
            tool_name: Tool 이름
        
        Returns:
            Tool 인스턴스 또는 None
        """
        tools = self.load_user_tools(user_id)
        for tool in tools:
            if tool.name == tool_name:
                return tool
        return None

