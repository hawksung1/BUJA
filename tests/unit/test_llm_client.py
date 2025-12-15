"""
LLM 클라이언트 단위 테스트
"""
import os
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.exceptions import LLMAPIError, LLMAPIKeyError, LLMProviderNotFoundError
from src.external.llm_client import (
    AnthropicProvider,
    LLMClient,
    OpenAIProvider,
    RateLimiter,
)


class TestRateLimiter:
    """RateLimiter 테스트"""

    @pytest.mark.asyncio
    async def test_rate_limiter_acquire(self):
        """Rate limit 획득 테스트"""
        limiter = RateLimiter(max_requests=2, time_window=60)

        # 첫 번째 요청 허용
        assert await limiter.acquire() is True

        # 두 번째 요청 허용
        assert await limiter.acquire() is True

        # 세 번째 요청 거부 (한도 초과)
        assert await limiter.acquire() is False


class TestOpenAIProvider:
    """OpenAIProvider 테스트"""

    def test_init_without_api_key(self):
        """API 키 없이 초기화 실패 테스트"""
        with unittest.mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(LLMAPIKeyError):
                OpenAIProvider("")

    @pytest.mark.asyncio
    async def test_generate_text_success(self):
        """텍스트 생성 성공 테스트"""
        with unittest.mock.patch("src.external.llm_client.AsyncOpenAI") as MockAsyncOpenAI:
            # Setup mock client
            mock_client = MockAsyncOpenAI.return_value
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Generated text"
            mock_response.choices[0].message.tool_calls = None
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            provider = OpenAIProvider("test-api-key")
            
            # Mock rate limiter
            provider.rate_limiter = MagicMock()
            provider.rate_limiter.wait_if_needed = AsyncMock()

            result = await provider.generate_text("Test prompt")

            assert result == "Generated text"
            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_text_api_error(self):
        """API 오류 테스트"""
        with unittest.mock.patch("src.external.llm_client.AsyncOpenAI") as MockAsyncOpenAI:
            mock_client = MockAsyncOpenAI.return_value
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))

            provider = OpenAIProvider("test-api-key")
            provider.rate_limiter = MagicMock()
            provider.rate_limiter.wait_if_needed = AsyncMock()

            with pytest.raises(LLMAPIError):
                await provider.generate_text("Test prompt")


class TestAnthropicProvider:
    """AnthropicProvider 테스트"""

    def test_init_without_api_key(self):
        """API 키 없이 초기화 실패 테스트"""
        with unittest.mock.patch.dict(os.environ, {}, clear=True):
            with pytest.raises(LLMAPIKeyError):
                AnthropicProvider("")

    @pytest.mark.asyncio
    async def test_generate_text_success(self):
        """텍스트 생성 성공 테스트"""
        with unittest.mock.patch("src.external.llm_client.AsyncAnthropic") as MockAsyncAnthropic:
            mock_client = MockAsyncAnthropic.return_value
            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "Generated text"
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            provider = AnthropicProvider("test-api-key")
            provider.rate_limiter = MagicMock()
            provider.rate_limiter.wait_if_needed = AsyncMock()

            result = await provider.generate_text("Test prompt")

            assert result == "Generated text"
            mock_client.messages.create.assert_called_once()


class TestLLMClient:
    """LLMClient 테스트"""

    def test_register_provider(self):
        """Provider 등록 테스트"""
        client = LLMClient()
        provider = OpenAIProvider("test-key")

        client.register_provider("openai", provider)

        assert "openai" in client.providers
        assert client.default_provider == "openai"

    def test_get_provider_success(self):
        """Provider 조회 성공 테스트"""
        client = LLMClient()
        provider = OpenAIProvider("test-key")

        client.register_provider("openai", provider)
        result = client.get_provider("openai")

        assert result == provider

    def test_get_provider_not_found(self):
        """Provider 조회 실패 테스트"""
        client = LLMClient()

        with pytest.raises(LLMProviderNotFoundError):
            client.get_provider("nonexistent")

    @pytest.mark.asyncio
    async def test_generate_text(self):
        """텍스트 생성 테스트"""
        client = LLMClient()
        provider = OpenAIProvider("test-key")

        # Mock provider
        provider.generate_text = AsyncMock(return_value="Generated text")
        client.register_provider("openai", provider)

        result = await client.generate_text("Test prompt", provider_name="openai")

        assert result == "Generated text"
        provider.generate_text.assert_called_once_with("Test prompt")

