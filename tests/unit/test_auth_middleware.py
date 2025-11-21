"""
AuthMiddleware 단위 테스트
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import streamlit as st

from src.exceptions import AuthenticationError
from src.middleware.auth_middleware import AuthMiddleware
from src.models import User


@pytest.fixture
def auth_middleware():
    """AuthMiddleware 인스턴스"""
    return AuthMiddleware()


class TestAuthMiddleware:
    """AuthMiddleware 테스트"""

    def test_is_authenticated_false(self, auth_middleware):
        """인증되지 않은 상태 테스트"""
        with patch.dict(st.session_state, {}, clear=True):
            assert auth_middleware.is_authenticated() is False

    def test_is_authenticated_true(self, auth_middleware):
        """인증된 상태 테스트"""
        user = User(id=1, email="test@example.com", password_hash="hash")
        with patch.dict(st.session_state, {"user": user}, clear=True):
            assert auth_middleware.is_authenticated() is True

    def test_get_current_user(self, auth_middleware):
        """현재 사용자 조회 테스트"""
        user = User(id=1, email="test@example.com", password_hash="hash")
        with patch.dict(st.session_state, {"user": user}, clear=True):
            current_user = auth_middleware.get_current_user()
            assert current_user == user

    def test_logout(self, auth_middleware):
        """로그아웃 테스트"""
        user = User(id=1, email="test@example.com", password_hash="hash")
        with patch.dict(st.session_state, {"user": user, "user_id": 1}, clear=True):
            auth_middleware.logout()
            assert "user" not in st.session_state
            assert "user_id" not in st.session_state

    @pytest.mark.asyncio
    async def test_login_success(self, auth_middleware):
        """로그인 성공 테스트"""
        user = User(id=1, email="test@example.com", password_hash="hash")

        mock_user_service = MagicMock()
        mock_user_service.authenticate = AsyncMock(return_value=user)
        auth_middleware.user_service = mock_user_service

        with patch.dict(st.session_state, {}, clear=True):
            result = await auth_middleware.login("test@example.com", "password")

            assert result == user
            assert st.session_state["user"] == user
            assert st.session_state["user_id"] == 1

    @pytest.mark.asyncio
    async def test_login_failure(self, auth_middleware):
        """로그인 실패 테스트"""
        mock_user_service = MagicMock()
        mock_user_service.authenticate = AsyncMock(side_effect=Exception("Invalid credentials"))
        auth_middleware.user_service = mock_user_service

        with pytest.raises(AuthenticationError):
            await auth_middleware.login("test@example.com", "wrong_password")

