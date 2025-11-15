"""
Base Tool 추상 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from config.logging import get_logger

logger = get_logger(__name__)


class BaseTool(ABC):
    """Tool 기본 클래스"""
    
    def __init__(self, name: str, description: str):
        """
        BaseTool 초기화
        
        Args:
            name: Tool 이름
            description: Tool 설명
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Tool 실행
        
        Args:
            **kwargs: Tool 실행에 필요한 파라미터
        
        Returns:
            실행 결과 딕셔너리
        """
        pass
    
    def get_function_schema(self) -> Dict[str, Any]:
        """
        Function Calling을 위한 스키마 반환
        
        Returns:
            OpenAI Function Calling 형식의 스키마
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema()
            }
        }
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        파라미터 스키마 반환
        
        Returns:
            JSON Schema 형식의 파라미터 정의
        """
        pass

