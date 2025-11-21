"""
Agent 단위 테스트
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.base_agent import ConversationMessage
from src.agents.investment_agent import InvestmentAgent
from src.external.llm_client import LLMClient


class TestConversationMessage:
    """ConversationMessage 테스트"""

    def test_conversation_message_creation(self):
        """대화 메시지 생성 테스트"""
        message = ConversationMessage("user", "Hello")

        assert message.role == "user"
        assert message.content == "Hello"
        assert message.timestamp is not None

    def test_conversation_message_to_dict(self):
        """대화 메시지 딕셔너리 변환 테스트"""
        message = ConversationMessage("assistant", "Hi there")
        message_dict = message.to_dict()

        assert message_dict["role"] == "assistant"
        assert message_dict["content"] == "Hi there"
        assert "timestamp" in message_dict


class TestBaseAgent:
    """BaseAgent 테스트"""

    def test_add_message(self):
        """메시지 추가 테스트"""
        agent = InvestmentAgent()

        agent.add_message("user", "Test message")

        assert len(agent.conversation_history) == 1
        assert agent.conversation_history[0].role == "user"
        assert agent.conversation_history[0].content == "Test message"

    def test_clear_history(self):
        """대화 기록 초기화 테스트"""
        agent = InvestmentAgent()

        agent.add_message("user", "Message 1")
        agent.add_message("assistant", "Message 2")

        assert len(agent.conversation_history) == 2

        agent.clear_history()

        assert len(agent.conversation_history) == 0

    def test_get_conversation_context(self):
        """대화 컨텍스트 가져오기 테스트"""
        agent = InvestmentAgent()

        agent.add_message("user", "Hello")
        agent.add_message("assistant", "Hi")

        context = agent.get_conversation_context()

        assert len(context) >= 2  # system prompt + messages
        assert context[-2]["role"] == "user"
        assert context[-1]["role"] == "assistant"


class TestInvestmentAgent:
    """InvestmentAgent 테스트"""

    @pytest.mark.asyncio
    async def test_chat_success(self):
        """채팅 성공 테스트"""
        agent = InvestmentAgent()

        # Mock LLM client
        mock_llm_client = MagicMock(spec=LLMClient)
        # chat()은 async generator를 반환하므로 generate_stream을 async generator로 mock
        async def mock_stream(*args, **kwargs):
            yield "This is a test response"
        mock_llm_client.generate_stream = mock_stream
        agent.llm_client = mock_llm_client

        # async generator를 수집
        response_chunks = []
        async for chunk in agent.chat("What should I invest in?"):
            response_chunks.append(chunk)
        response = "".join(response_chunks)

        assert response == "This is a test response"
        assert len(agent.conversation_history) == 2  # user + assistant

    @pytest.mark.asyncio
    async def test_chat_with_context(self):
        """컨텍스트 포함 채팅 테스트"""
        agent = InvestmentAgent()

        mock_llm_client = MagicMock(spec=LLMClient)
        # chat()은 async generator를 반환하므로 generate_stream을 async generator로 mock
        async def mock_stream(*args, **kwargs):
            yield "Response"
        mock_llm_client.generate_stream = mock_stream
        agent.llm_client = mock_llm_client

        context = {
            "user_profile": {"name": "Test User", "age": 30},
            "investment_preference": {"risk_tolerance": 7}
        }

        # async generator를 수집
        response_chunks = []
        async for chunk in agent.chat("What should I invest in?", context=context):
            response_chunks.append(chunk)
        response = "".join(response_chunks)

        assert response == "Response"

    @pytest.mark.asyncio
    async def test_analyze_image(self):
        """이미지 분석 테스트"""
        agent = InvestmentAgent()

        mock_llm_client = MagicMock(spec=LLMClient)
        mock_llm_client.analyze_image = AsyncMock(return_value='{"analysis": "test"}')
        agent.llm_client = mock_llm_client

        image_data = b"fake image data"

        result = await agent.analyze_image(image_data=image_data)

        assert result["status"] == "success"
        mock_llm_client.analyze_image.assert_called_once()

