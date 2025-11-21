"""
기본 기능 통합 테스트
실제 사용 시나리오를 기반으로 한 기본 기능 검증
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    ValidationError,
)
from src.middleware.auth_middleware import AuthMiddleware
from src.models import User
from src.services import ChatService, UserService


class TestBasicAuthFlow:
    """기본 인증 플로우 테스트"""

    @pytest.fixture
    def auth_middleware(self):
        return AuthMiddleware()

    @pytest.fixture
    def mock_user_service(self):
        service = MagicMock()
        return service

    @pytest.mark.asyncio
    async def test_complete_login_flow(self, auth_middleware, mock_user_service):
        """완전한 로그인 플로우 테스트"""
        # 1. 초기 상태: 인증되지 않음
        with patch.dict("streamlit.session_state", {}, clear=True):
            assert auth_middleware.is_authenticated() is False

            # 2. 로그인 시도
            user = User(id=1, email="test@example.com", password_hash="hash")
            mock_user_service.authenticate = AsyncMock(return_value=user)
            auth_middleware.user_service = mock_user_service

            result = await auth_middleware.login("test@example.com", "password")

            # 3. 로그인 성공 확인
            assert result == user
            assert auth_middleware.is_authenticated() is True
            assert auth_middleware.get_current_user() == user

            # 4. 로그아웃
            auth_middleware.logout()
            assert auth_middleware.is_authenticated() is False

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, auth_middleware, mock_user_service):
        """잘못된 비밀번호로 로그인 시도"""
        mock_user_service.authenticate = AsyncMock(side_effect=InvalidCredentialsError("Invalid password"))
        auth_middleware.user_service = mock_user_service

        with patch.dict("streamlit.session_state", {}, clear=True):
            with pytest.raises(AuthenticationError):
                await auth_middleware.login("test@example.com", "wrong_password")

            # 인증되지 않은 상태 유지
            assert auth_middleware.is_authenticated() is False

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_user(self, auth_middleware, mock_user_service):
        """존재하지 않는 사용자로 로그인 시도"""
        mock_user_service.authenticate = AsyncMock(side_effect=UserNotFoundError("User not found"))
        auth_middleware.user_service = mock_user_service

        with patch.dict("streamlit.session_state", {}, clear=True):
            with pytest.raises(AuthenticationError):
                await auth_middleware.login("nonexistent@example.com", "password")

            assert auth_middleware.is_authenticated() is False


class TestBasicUserServiceFlow:
    """기본 사용자 서비스 플로우 테스트"""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        mock_session = AsyncMock()
        db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        return db

    @pytest.fixture
    def user_service(self, mock_db):
        return UserService(database=mock_db)

    @pytest.mark.asyncio
    async def test_user_registration_flow(self, user_service, mock_db):
        """사용자 등록 플로우 테스트"""
        # 1. 새 사용자 생성
        new_user = User(id=1, email="newuser@example.com", password_hash="hashed")

        mock_user_repo = MagicMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=None)  # 중복 없음
        mock_user_repo.create_user = AsyncMock(return_value=new_user)
        user_service.user_repo = mock_user_repo

        # 2. 회원가입
        result = await user_service.register(
            email="newuser@example.com",
            password="password123"
        )

        # 3. 검증
        assert result.email == "newuser@example.com"
        mock_user_repo.get_by_email.assert_called_once_with("newuser@example.com")
        mock_user_repo.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_registration_duplicate_email(self, user_service):
        """중복 이메일로 회원가입 시도"""
        existing_user = User(id=1, email="existing@example.com", password_hash="hash")

        mock_user_repo = MagicMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=existing_user)
        user_service.user_repo = mock_user_repo

        with pytest.raises(UserAlreadyExistsError):
            await user_service.register(
                email="existing@example.com",
                password="password123"
            )

    @pytest.mark.asyncio
    async def test_user_registration_invalid_email(self, user_service):
        """유효하지 않은 이메일로 회원가입 시도"""
        with pytest.raises(ValidationError):
            await user_service.register(
                email="invalid-email",
                password="password123"
            )

    @pytest.mark.asyncio
    async def test_user_registration_weak_password(self, user_service):
        """약한 비밀번호로 회원가입 시도"""
        with pytest.raises(ValidationError):
            await user_service.register(
                email="test@example.com",
                password="123"  # 너무 짧음
            )

    @pytest.mark.asyncio
    async def test_user_authentication_flow(self, user_service):
        """사용자 인증 플로우 테스트"""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$hashedpassword",
            is_active=True
        )

        mock_user_repo = MagicMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        with patch("src.services.user_service.verify_password", return_value=True):
            result = await user_service.authenticate(
                email="test@example.com",
                password="password123"
            )

            assert result == user
            assert result.email == "test@example.com"
            assert result.is_active is True

    @pytest.mark.asyncio
    async def test_user_authentication_inactive_account(self, user_service):
        """비활성 계정 인증 시도"""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$hashedpassword",
            is_active=False  # 비활성 계정
        )

        mock_user_repo = MagicMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=user)
        user_service.user_repo = mock_user_repo

        with patch("src.services.user_service.verify_password", return_value=True):
            with pytest.raises(InvalidCredentialsError):
                await user_service.authenticate(
                    email="test@example.com",
                    password="password123"
                )


class TestBasicChatServiceFlow:
    """기본 채팅 서비스 플로우 테스트"""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        mock_session = AsyncMock()
        db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        return db

    @pytest.fixture
    def chat_service(self, mock_db):
        return ChatService(database=mock_db)

    @pytest.mark.asyncio
    async def test_chat_message_flow(self, chat_service):
        """채팅 메시지 플로우 테스트"""
        from src.models.chat import ChatMessage

        # 1. 사용자 메시지 저장
        user_message = ChatMessage(
            id=1, user_id=1, role="user", content="Hello"
        )

        mock_chat_repo = MagicMock()
        mock_chat_repo.create_message = AsyncMock(return_value=user_message)
        chat_service.chat_repo = mock_chat_repo

        saved_msg = await chat_service.save_message(
            user_id=1,
            role="user",
            content="Hello"
        )

        assert saved_msg.content == "Hello"
        assert saved_msg.role == "user"

        # 2. 어시스턴트 메시지 저장
        assistant_message = ChatMessage(
            id=2, user_id=1, role="assistant", content="Hi there!"
        )
        mock_chat_repo.create_message = AsyncMock(return_value=assistant_message)

        saved_msg = await chat_service.save_message(
            user_id=1,
            role="assistant",
            content="Hi there!"
        )

        assert saved_msg.content == "Hi there!"
        assert saved_msg.role == "assistant"

    @pytest.mark.asyncio
    async def test_chat_message_retrieval(self, chat_service):
        """채팅 메시지 조회 테스트"""
        from src.models.chat import ChatMessage

        messages = [
            ChatMessage(id=1, user_id=1, role="user", content="Hello"),
            ChatMessage(id=2, user_id=1, role="assistant", content="Hi there!"),
        ]

        mock_chat_repo = MagicMock()
        mock_chat_repo.get_by_user_id = AsyncMock(return_value=messages)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.get_messages(1)

        assert len(result) == 2
        # 메시지가 역순으로 반환될 수 있으므로 내용으로 확인
        roles = [msg["role"] for msg in result]
        contents = [msg["content"] for msg in result]
        assert "user" in roles
        assert "assistant" in roles
        assert "Hello" in contents
        assert "Hi there!" in contents

    @pytest.mark.asyncio
    async def test_chat_message_with_image(self, chat_service):
        """이미지가 포함된 채팅 메시지 테스트"""
        import base64

        from src.models.chat import ChatMessage

        image_data = base64.b64encode(b"fake image data").decode('utf-8')
        message = ChatMessage(
            id=1, user_id=1, role="user", content="Check this image",
            image_data=image_data, image_caption="Test image"
        )

        mock_chat_repo = MagicMock()
        mock_chat_repo.create_message = AsyncMock(return_value=message)
        chat_service.chat_repo = mock_chat_repo

        result = await chat_service.save_message(
            user_id=1,
            role="user",
            content="Check this image",
            image_data=b"fake image data",
            image_caption="Test image"
        )

        assert result.image_data == image_data
        assert result.image_caption == "Test image"


class TestBasicIntegrationFlow:
    """기본 통합 플로우 테스트"""

    @pytest.mark.asyncio
    async def test_user_registration_and_login_flow(self):
        """사용자 등록 후 로그인 플로우"""
        from src.middleware.auth_middleware import AuthMiddleware
        from src.services import UserService

        mock_db = MagicMock()
        mock_session = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        user_service = UserService(database=mock_db)
        auth_middleware = AuthMiddleware()

        # 1. 회원가입
        new_user = User(id=1, email="newuser@example.com", password_hash="hashed", is_active=True)
        mock_user_repo = MagicMock()
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        mock_user_repo.create_user = AsyncMock(return_value=new_user)
        user_service.user_repo = mock_user_repo

        registered_user = await user_service.register(
            email="newuser@example.com",
            password="password123"
        )

        assert registered_user.email == "newuser@example.com"

        # 2. 로그인 (활성화된 계정으로)
        active_user = User(id=1, email="newuser@example.com", password_hash="hashed", is_active=True)
        mock_user_repo.get_by_email = AsyncMock(return_value=active_user)
        user_service.user_repo = mock_user_repo
        auth_middleware.user_service = user_service

        with patch("src.services.user_service.verify_password", return_value=True):
            with patch.dict("streamlit.session_state", {}, clear=True):
                logged_in_user = await auth_middleware.login(
                    "newuser@example.com",
                    "password123"
                )

                assert logged_in_user == active_user
                assert auth_middleware.is_authenticated() is True


class TestBasicErrorHandling:
    """기본 에러 처리 테스트"""

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self):
        """인증 에러 처리 테스트"""
        auth_middleware = AuthMiddleware()
        mock_user_service = MagicMock()
        mock_user_service.authenticate = AsyncMock(side_effect=Exception("Database error"))
        auth_middleware.user_service = mock_user_service

        with patch.dict("streamlit.session_state", {}, clear=True):
            with pytest.raises(AuthenticationError):
                await auth_middleware.login("test@example.com", "password")

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """검증 에러 처리 테스트"""
        from src.services import UserService

        mock_db = MagicMock()
        user_service = UserService(database=mock_db)

        # 유효하지 않은 이메일
        with pytest.raises(ValidationError):
            await user_service.register(
                email="",
                password="password123"
            )

        # 유효하지 않은 비밀번호
        with pytest.raises(ValidationError):
            await user_service.register(
                email="test@example.com",
                password=""  # 빈 비밀번호
            )


class TestBasicDataValidation:
    """기본 데이터 검증 테스트"""

    @pytest.mark.asyncio
    async def test_email_validation(self):
        """이메일 검증 테스트"""
        from src.services import UserService

        mock_db = MagicMock()
        user_service = UserService(database=mock_db)

        # 유효하지 않은 이메일들 (ValidationError 또는 UserAlreadyExistsError 발생 가능)
        invalid_emails = [
            "",
            "not-an-email",
            "@example.com",
            "test@",
        ]

        for email in invalid_emails:
            with pytest.raises((ValidationError, UserAlreadyExistsError)):
                mock_user_repo = MagicMock()
                # 빈 이메일이나 잘못된 형식은 ValidationError
                if email == "":
                    # validate_email이 먼저 호출되므로 ValidationError 발생
                    pass
                else:
                    mock_user_repo.get_by_email = AsyncMock(return_value=None)
                user_service.user_repo = mock_user_repo

                await user_service.register(
                    email=email,
                    password="password123"
                )

    @pytest.mark.asyncio
    async def test_password_validation(self):
        """비밀번호 검증 테스트"""
        from src.services import UserService

        mock_db = MagicMock()
        user_service = UserService(database=mock_db)

        # 약한 비밀번호들
        weak_passwords = [
            "",
            "123",
            "abc",
            "password",  # 너무 일반적
        ]

        for password in weak_passwords:
            with pytest.raises(ValidationError):
                await user_service.register(
                    email="test@example.com",
                    password=password
                )

