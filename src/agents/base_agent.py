"""
Base Agent 추상 클래스
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.external.llm_client import BaseLLMProvider, LLMClient
from config.logging import get_logger

logger = get_logger(__name__)


class ConversationMessage:
    """대화 메시지"""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        대화 메시지 초기화
        
        Args:
            role: 역할 (user, assistant, system)
            content: 메시지 내용
            timestamp: 타임스탬프 (기본값: 현재 시간)
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """Agent 기본 클래스"""
    
    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        llm_client: Optional[LLMClient] = None,
        system_prompt: Optional[str] = None
    ):
        """
        BaseAgent 초기화
        
        Args:
            llm_provider: LLM Provider 인스턴스 (선택사항)
            llm_client: LLM Client 인스턴스 (선택사항)
            system_prompt: 시스템 프롬프트 (선택사항)
        """
        if llm_provider:
            self.llm_provider = llm_provider
        elif llm_client:
            self.llm_client = llm_client
        else:
            from src.external.llm_client import get_llm_client
            self.llm_client = get_llm_client()
        
        self.system_prompt = system_prompt
        self.conversation_history: List[ConversationMessage] = []
        self.max_history_length = 20  # 최대 대화 기록 길이
    
    def add_message(self, role: str, content: str) -> None:
        """
        대화 기록에 메시지 추가
        
        Args:
            role: 역할 (user, assistant, system)
            content: 메시지 내용
        """
        # content가 None이면 빈 문자열로 변환 (OpenAI API는 null content를 허용하지 않음)
        if content is None:
            content = ""
        message = ConversationMessage(role=role, content=content)
        self.conversation_history.append(message)
        
        # 최대 길이 초과 시 오래된 메시지 제거
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def get_conversation_context(self) -> List[Dict[str, str]]:
        """
        대화 컨텍스트 가져오기 (LLM API 형식)
        
        Returns:
            메시지 리스트
        """
        messages = []
        
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        for msg in self.conversation_history:
            # content가 None이면 빈 문자열로 변환 (OpenAI API는 null content를 허용하지 않음)
            content = msg.content if msg.content is not None else ""
            messages.append({"role": msg.role, "content": content})
        
        return messages
    
    def clear_history(self) -> None:
        """대화 기록 초기화"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    @abstractmethod
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        사용자 메시지에 대한 응답 생성
        
        Args:
            message: 사용자 메시지
            context: 추가 컨텍스트 (선택사항)
        
        Returns:
            Agent 응답
        """
        pass
    
    @abstractmethod
    async def analyze_image(
        self,
        image_path: Optional[str] = None,
        image_data: Optional[bytes] = None,
        prompt: str = "이 이미지를 분석해주세요."
    ) -> Dict[str, Any]:
        """
        이미지 분석
        
        Args:
            image_path: 이미지 파일 경로 (선택사항)
            image_data: 이미지 바이너리 데이터 (선택사항)
            prompt: 분석 프롬프트
        
        Returns:
            분석 결과 딕셔너리
        """
        pass

