"""
LLM 클라이언트 구현
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, AsyncGenerator, Callable, Tuple
from enum import Enum
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from config.settings import settings
from src.exceptions import (
    LLMAPIError,
    LLMProviderNotFoundError,
    LLMAPIKeyError,
)
from config.logging import get_logger

logger = get_logger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    retryable_exceptions: tuple = (LLMAPIError, httpx.HTTPError, Exception)
):
    """
    재시도 데코레이터
    
    Args:
        max_retries: 최대 재시도 횟수
        backoff_factor: 백오프 배수 (지수 백오프)
        retryable_exceptions: 재시도할 예외 타입
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(
                            f"LLM API call failed (attempt {attempt + 1}/{max_retries + 1}), "
                            f"retrying in {wait_time}s: {str(e)}"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"LLM API call failed after {max_retries + 1} attempts: {str(e)}")
                        raise
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


class LLMProvider(str, Enum):
    """LLM 제공자 열거형"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class RateLimiter:
    """Rate Limiting 관리"""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Rate Limiter 초기화
        
        Args:
            max_requests: 시간 창 내 최대 요청 수
            time_window: 시간 창 (초)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def acquire(self, key: str = "default") -> bool:
        """
        Rate limit 확인 및 획득
        
        Args:
            key: Rate limit 키 (기본값: "default")
        
        Returns:
            요청 허용 여부
        """
        async with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.time_window)
            
            # 오래된 요청 제거
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            # Rate limit 확인
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # 요청 추가
            self.requests[key].append(now)
            return True
    
    async def wait_if_needed(self, key: str = "default") -> None:
        """
        Rate limit에 도달한 경우 대기
        
        Args:
            key: Rate limit 키
        """
        while not await self.acquire(key):
            await asyncio.sleep(1)


class BaseLLMProvider(ABC):
    """LLM Provider 기본 클래스"""
    
    def __init__(self, api_key: str, rate_limiter: Optional[RateLimiter] = None):
        """
        LLM Provider 초기화
        
        Args:
            api_key: API 키
            rate_limiter: Rate limiter (선택사항)
        """
        if not api_key:
            raise LLMAPIKeyError(f"{self.__class__.__name__} API key is not set.")
        
        self.api_key = api_key
        self.rate_limiter = rate_limiter or RateLimiter(max_requests=60, time_window=60)
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        텍스트 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트 (선택사항)
            max_tokens: 최대 토큰 수
            temperature: 온도 (0.0-2.0)
            **kwargs: 추가 파라미터
        
        Returns:
            생성된 텍스트
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        스트리밍 텍스트 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트 (선택사항)
            max_tokens: 최대 토큰 수
            temperature: 온도 (0.0-2.0)
            **kwargs: 추가 파라미터
        
        Yields:
            생성된 텍스트 청크
        """
        pass
    
    @abstractmethod
    async def analyze_image(
        self,
        image_url: Optional[str] = None,
        image_data: Optional[bytes] = None,
        prompt: str = "이 이미지를 분석해주세요.",
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        이미지 분석 (Vision API)
        
        Args:
            image_url: 이미지 URL (선택사항)
            image_data: 이미지 바이너리 데이터 (선택사항)
            prompt: 분석 프롬프트
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터
        
        Returns:
            분석 결과 텍스트
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider 구현"""
    
    def __init__(self, api_key: str, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(api_key, rate_limiter)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"  # 기본 모델
    
    @retry_on_failure(max_retries=3, backoff_factor=1.0)
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> str:
        """텍스트 생성 (Function Calling 지원)"""
        await self.rate_limiter.wait_if_needed()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            create_params = {
                "model": model or self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            
            # Function Calling 지원
            if tools:
                create_params["tools"] = tools
                if tool_choice:
                    create_params["tool_choice"] = tool_choice
            
            create_params.update(kwargs)
            
            response = await self.client.chat.completions.create(**create_params)
            
            message = response.choices[0].message
            
            # Function calling 응답인 경우
            if message.tool_calls:
                # content가 None일 수 있으므로 빈 문자열로 변환
                content = message.content if message.content is not None else ""
                return {
                    "content": content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",  # OpenAI API 필수 필드
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                }
            
            return message.content or ""
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMAPIError(f"OpenAI API call failed: {str(e)}")
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """스트리밍 텍스트 생성"""
        await self.rate_limiter.wait_if_needed()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = await self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI API streaming error: {e}")
            raise LLMAPIError(f"OpenAI API streaming call failed: {str(e)}")
    
    async def analyze_image(
        self,
        image_url: Optional[str] = None,
        image_data: Optional[bytes] = None,
        prompt: str = "이 이미지를 분석해주세요.",
        max_tokens: int = 2000,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """이미지 분석 (GPT-4 Vision)"""
        await self.rate_limiter.wait_if_needed()
        
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }]
        
        # 이미지 추가
        if image_url:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        elif image_data:
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        else:
            raise ValueError("image_url 또는 image_data 중 하나는 필수입니다.")
        
        try:
            response = await self.client.chat.completions.create(
                model=model or "gpt-4o",
                messages=messages,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI Vision API error: {e}")
            raise LLMAPIError(f"OpenAI Vision API call failed: {str(e)}")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Provider 구현"""
    
    def __init__(self, api_key: str, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(api_key, rate_limiter)
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"  # 기본 모델
    
    @retry_on_failure(max_retries=3, backoff_factor=1.0)
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """텍스트 생성"""
        await self.rate_limiter.wait_if_needed()
        
        try:
            response = await self.client.messages.create(
                model=model or self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise LLMAPIError(f"Anthropic API call failed: {str(e)}")
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """스트리밍 텍스트 생성"""
        await self.rate_limiter.wait_if_needed()
        
        try:
            with await self.client.messages.stream(
                model=model or self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic API streaming error: {e}")
            raise LLMAPIError(f"Anthropic API streaming call failed: {str(e)}")
    
    async def analyze_image(
        self,
        image_url: Optional[str] = None,
        image_data: Optional[bytes] = None,
        prompt: str = "이 이미지를 분석해주세요.",
        max_tokens: int = 2000,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """이미지 분석 (Claude Vision)"""
        await self.rate_limiter.wait_if_needed()
        
        # 이미지 데이터 준비
        if image_data:
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            image_source = {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": base64_image
            }
        elif image_url:
            # URL에서 이미지 다운로드
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content
                import base64
                base64_image = base64.b64encode(image_data).decode('utf-8')
                image_source = {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64_image
                }
        else:
            raise ValueError("image_url 또는 image_data 중 하나는 필수입니다.")
        
        try:
            response = await self.client.messages.create(
                model=model or self.model,
                max_tokens=max_tokens,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": image_source},
                        {"type": "text", "text": prompt}
                    ]
                }],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic Vision API error: {e}")
            raise LLMAPIError(f"Anthropic Vision API call failed: {str(e)}")


class LLMClient:
    """LLM 클라이언트 (Provider 관리)"""
    
    def __init__(self):
        """LLMClient 초기화"""
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider: Optional[str] = None
    
    def register_provider(
        self,
        provider_name: str,
        provider: BaseLLMProvider,
        set_as_default: bool = False
    ) -> None:
        """
        Provider 등록
        
        Args:
            provider_name: Provider 이름
            provider: Provider 인스턴스
            set_as_default: 기본 Provider로 설정할지 여부
        """
        self.providers[provider_name] = provider
        if set_as_default or not self.default_provider:
            self.default_provider = provider_name
        logger.info(f"LLM Provider registered: {provider_name}")
    
    def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        """
        Provider 조회
        
        Args:
            provider_name: Provider 이름 (기본값: 기본 Provider)
        
        Returns:
            Provider 인스턴스
        
        Raises:
            LLMProviderNotFoundError: Provider를 찾을 수 없는 경우
        """
        name = provider_name or self.default_provider
        if not name:
            raise LLMProviderNotFoundError("Default LLM Provider is not set.")
        
        if name not in self.providers:
            raise LLMProviderNotFoundError(f"LLM Provider not found: {name}")
        
        return self.providers[name]
    
    async def generate_text(
        self,
        prompt: str,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        텍스트 생성
        
        Args:
            prompt: 사용자 프롬프트
            provider_name: Provider 이름 (선택사항)
            **kwargs: 추가 파라미터
        
        Returns:
            생성된 텍스트
        """
        provider = self.get_provider(provider_name)
        return await provider.generate_text(prompt, **kwargs)
    
    async def generate_stream(
        self,
        prompt: str,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        스트리밍 텍스트 생성
        
        Args:
            prompt: 사용자 프롬프트
            provider_name: Provider 이름 (선택사항)
            **kwargs: 추가 파라미터
        
        Yields:
            생성된 텍스트 청크
        """
        provider = self.get_provider(provider_name)
        async for chunk in provider.generate_stream(prompt, **kwargs):
            yield chunk
    
    async def analyze_image(
        self,
        image_url: Optional[str] = None,
        image_data: Optional[bytes] = None,
        prompt: str = "이 이미지를 분석해주세요.",
        provider_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        이미지 분석
        
        Args:
            image_url: 이미지 URL (선택사항)
            image_data: 이미지 바이너리 데이터 (선택사항)
            prompt: 분석 프롬프트
            provider_name: Provider 이름 (선택사항)
            **kwargs: 추가 파라미터
        
        Returns:
            분석 결과 텍스트
        """
        provider = self.get_provider(provider_name)
        return await provider.analyze_image(
            image_url=image_url,
            image_data=image_data,
            prompt=prompt,
            **kwargs
        )


# 전역 LLM 클라이언트 인스턴스
_llm_client: Optional[LLMClient] = None


def _get_user_api_keys() -> Tuple[Optional[str], Optional[str]]:
    """
    사용자 입력 API 키 가져오기 (session_state에서)
    
    Returns:
        (openai_api_key, anthropic_api_key) 튜플
    """
    try:
        import streamlit as st
        user_openai_key = st.session_state.get("user_openai_api_key", "")
        user_anthropic_key = st.session_state.get("user_anthropic_api_key", "")
        
        # 빈 문자열이면 None으로 변환
        openai_key = user_openai_key if user_openai_key else None
        anthropic_key = user_anthropic_key if user_anthropic_key else None
        
        return openai_key, anthropic_key
    except Exception:
        # Streamlit이 없는 환경에서는 None 반환
        return None, None


def get_llm_client() -> LLMClient:
    """
    전역 LLM 클라이언트 인스턴스 가져오기
    사용자 입력 API 키가 있으면 우선 사용, 없으면 환경 변수 값 사용
    
    Returns:
        LLMClient 인스턴스
    
    Raises:
        LLMProviderNotFoundError: API 키가 설정되지 않은 경우
    """
    global _llm_client
    
    # 사용자 입력 API 키 가져오기
    user_openai_key, user_anthropic_key = _get_user_api_keys()
    
    # 사용자 입력 키가 있으면 우선 사용, 없으면 환경 변수 값 사용
    openai_api_key = user_openai_key or settings.openai_api_key
    anthropic_api_key = user_anthropic_key or settings.anthropic_api_key
    
    # 클라이언트가 없거나 재로드가 필요한 경우 초기화
    needs_reload = False
    try:
        import streamlit as st
        needs_reload = st.session_state.get("llm_client_needs_reload", False)
        if needs_reload:
            st.session_state.llm_client_needs_reload = False
    except Exception:
        pass
    
    if _llm_client is None or needs_reload:
        _llm_client = LLMClient()
        
        # OpenAI Provider 등록
        if openai_api_key:
            try:
                openai_provider = OpenAIProvider(openai_api_key)
                _llm_client.register_provider(
                    LLMProvider.OPENAI.value,
                    openai_provider,
                    set_as_default=(settings.default_llm_provider == "openai")
                )
                logger.info("OpenAI Provider registered (user input or env)")
            except Exception as e:
                logger.error(f"Failed to register OpenAI Provider: {e}")
        
        # Anthropic Provider 등록
        if anthropic_api_key:
            try:
                anthropic_provider = AnthropicProvider(anthropic_api_key)
                _llm_client.register_provider(
                    LLMProvider.ANTHROPIC.value,
                    anthropic_provider,
                    set_as_default=(settings.default_llm_provider == "anthropic")
                )
                logger.info("Anthropic Provider registered (user input or env)")
            except Exception as e:
                logger.error(f"Failed to register Anthropic Provider: {e}")
        
        # Provider가 하나도 등록되지 않은 경우
        if not _llm_client.providers:
            logger.warning("No LLM API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env.local or enter in the sidebar")
    
    return _llm_client

