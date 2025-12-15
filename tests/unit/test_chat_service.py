"""
ChatService 단위 테스트
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.database import Database
from src.models.chat import ChatMessage
from src.services.chat_service import ChatService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def chat_service(mock_db):
    """ChatService 인스턴스"""
    return ChatService(database=mock_db)


class TestChatServiceGetMessages:
    """ChatService.get_messages 테스트"""

    @pytest.mark.asyncio
    async def test_get_messages_success(self, chat_service):
        """메시지 조회 성공 테스트"""
        messages = [
            ChatMessage(
                id=2, user_id=1, role="assistant", content="Hi there",
                project_id=None
            ),
            ChatMessage(
                id=1, user_id=1, role="user", content="Hello",
                project_id=None
            )
        ]

        mock_chat_repo = MagicMock()
        mock_chat_repo.get_by_user_id = AsyncMock(return_value=messages)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.get_messages(1)

        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"
        assert result[1]["role"] == "assistant"
        assert result[1]["content"] == "Hi there"
        mock_chat_repo.get_by_user_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_messages_with_limit(self, chat_service):
        """제한된 개수의 메시지 조회 테스트"""
        messages = [
            ChatMessage(id=i, user_id=1, role="user", content=f"Message {i}")
            for i in range(1, 6)
        ]

        mock_chat_repo = MagicMock()
        mock_chat_repo.get_by_user_id = AsyncMock(return_value=messages[:3])
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.get_messages(1, limit=3)

        assert len(result) == 3
        mock_chat_repo.get_by_user_id.assert_called_once_with(1, limit=3, project_id=None, session=None)

    @pytest.mark.asyncio
    async def test_get_messages_with_project_id(self, chat_service):
        """프로젝트별 메시지 조회 테스트"""
        messages = [
            ChatMessage(
                id=1, user_id=1, role="user", content="Hello",
                project_id=1
            )
        ]

        mock_chat_repo = MagicMock()
        mock_chat_repo.get_by_user_id = AsyncMock(return_value=messages)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.get_messages(1, project_id=1)

        assert len(result) == 1
        mock_chat_repo.get_by_user_id.assert_called_once_with(1, limit=None, project_id=1, session=None)

    @pytest.mark.asyncio
    async def test_get_messages_with_image(self, chat_service):
        """이미지가 포함된 메시지 조회 테스트"""
        import base64
        image_data = base64.b64encode(b"fake image data").decode('utf-8')

        messages = [
            ChatMessage(
                id=1, user_id=1, role="user", content="Check this image",
                image_data=image_data, image_caption="Test image"
            )
        ]

        mock_chat_repo = MagicMock()
        mock_chat_repo.get_by_user_id = AsyncMock(return_value=messages)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.get_messages(1)

        assert len(result) == 1
        assert "image" in result[0]
        assert result[0]["image_caption"] == "Test image"


class TestChatServiceSaveMessage:
    """ChatService.save_message 테스트"""

    @pytest.mark.asyncio
    async def test_save_message_success(self, chat_service):
        """메시지 저장 성공 테스트"""
        message = ChatMessage(
            id=1, user_id=1, role="user", content="Hello"
        )

        mock_chat_repo = MagicMock()
        mock_chat_repo.create_message = AsyncMock(return_value=message)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.save_message(
            user_id=1,
            role="user",
            content="Hello"
        )

        assert result == message
        assert result.content == "Hello"
        mock_chat_repo.create_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_message_with_image_bytes(self, chat_service):
        """바이트 이미지가 포함된 메시지 저장 테스트"""
        import base64
        image_bytes = b"fake image data"
        message = ChatMessage(
            id=1, user_id=1, role="user", content="Check this",
            image_data=base64.b64encode(image_bytes).decode('utf-8')
        )

        mock_chat_repo = MagicMock()
        mock_chat_repo.create_message = AsyncMock(return_value=message)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.save_message(
            user_id=1,
            role="user",
            content="Check this",
            image_data=image_bytes
        )

        assert result == message
        # 바이트가 base64로 변환되었는지 확인
        call_args = mock_chat_repo.create_message.call_args
        assert isinstance(call_args[1]["image_data"], str)

    @pytest.mark.asyncio
    async def test_save_message_with_project_id(self, chat_service):
        """프로젝트 ID가 포함된 메시지 저장 테스트"""
        message = ChatMessage(
            id=1, user_id=1, role="user", content="Hello",
            project_id=1
        )

        mock_chat_repo = MagicMock()
        mock_chat_repo.create_message = AsyncMock(return_value=message)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.save_message(
            user_id=1,
            role="user",
            content="Hello",
            project_id=1
        )

        assert result.project_id == 1
        call_args = mock_chat_repo.create_message.call_args
        assert call_args[1]["project_id"] == 1


class TestChatServiceClearMessages:
    """ChatService.clear_messages 테스트"""

    @pytest.mark.asyncio
    async def test_clear_messages_all(self, chat_service):
        """모든 메시지 삭제 테스트"""
        mock_chat_repo = MagicMock()
        mock_chat_repo.delete_by_user_id = AsyncMock(return_value=5)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.clear_messages(1)

        assert result == 5
        mock_chat_repo.delete_by_user_id.assert_called_once_with(1, session=None)

    @pytest.mark.asyncio
    async def test_clear_messages_by_project(self, chat_service, mock_db):
        """프로젝트별 메시지 삭제 테스트"""

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.rowcount = 3
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await chat_service.clear_messages(1, project_id=1)

        assert result == 3
        mock_session.execute.assert_called_once()


class TestChatServiceSearchMessages:
    """ChatService.search_messages 테스트"""

    @pytest.mark.asyncio
    async def test_search_messages_success(self, chat_service, mock_db):
        """메시지 검색 성공 테스트"""
        messages = [
            ChatMessage(
                id=1, user_id=1, role="user",
                content="Hello, how are you?"
            ),
            ChatMessage(
                id=2, user_id=1, role="assistant",
                content="I'm doing well, thank you!"
            )
        ]

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=messages)
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await chat_service.search_messages(1, "Hello")

        assert len(result) == 2
        assert any("Hello" in msg["content"] for msg in result)

    @pytest.mark.asyncio
    async def test_search_messages_with_project_id(self, chat_service, mock_db):
        """프로젝트별 메시지 검색 테스트"""
        messages = [
            ChatMessage(
                id=1, user_id=1, role="user",
                content="Project message", project_id=1
            )
        ]

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=messages)
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await chat_service.search_messages(1, "Project", project_id=1)

        assert len(result) == 1
        assert result[0]["content"] == "Project message"

    @pytest.mark.asyncio
    async def test_search_messages_with_limit(self, chat_service, mock_db):
        """제한된 개수의 검색 결과 테스트"""
        messages = [
            ChatMessage(
                id=i, user_id=1, role="user",
                content=f"Message {i} with keyword"
            )
            for i in range(1, 6)
        ]

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=messages[:3])
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await chat_service.search_messages(1, "keyword", limit=3)

        assert len(result) == 3

