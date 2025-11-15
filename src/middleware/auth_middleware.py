"""
인증 미들웨어 (Streamlit용)
"""
from typing import Optional, Callable, Any
import logging
import streamlit as st
from src.services.user_service import UserService
from src.models import User
from src.exceptions import AuthenticationError, UserNotFoundError
from config.logging import get_logger

logger = get_logger(__name__)


class AuthMiddleware:
    """인증 미들웨어"""
    
    def __init__(self, user_service: Optional[UserService] = None):
        """
        AuthMiddleware 초기화
        
        Args:
            user_service: UserService 인스턴스 (기본값: 새 인스턴스 생성)
        """
        self.user_service = user_service or UserService()
    
    def get_current_user(self) -> Optional[User]:
        """
        현재 로그인한 사용자 조회 (Streamlit Session State)
        새로고침 후에도 세션 상태가 유지되도록 처리
        
        Returns:
            현재 사용자 또는 None
        """
        # 디버깅: 세션 상태 확인 (상세 디버깅이 필요한 경우에만)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Session state keys: {list(st.session_state.keys())}")
            logger.debug(f"user_id in session: {'user_id' in st.session_state}")
            logger.debug(f"user in session: {'user' in st.session_state}")
        
        # Streamlit 세션 상태는 새로고침 시 초기화될 수 있으므로
        # 초기화 플래그를 확인하여 복원 시도
        if "_session_restored" not in st.session_state:
            # 세션이 새로 시작된 경우, 이전 세션 정보 복원 시도
            # Streamlit은 세션 상태를 자동으로 복원하므로, 여기서는 로깅만 수행
            st.session_state._session_restored = True
            logger.debug("Session restored, checking for user_id")
        
        # user_id가 있으면 먼저 확인 (새로고침 후에도 유지되어야 함)
        if "user_id" in st.session_state:
            user_id = st.session_state.user_id
            logger.debug(f"Found user_id in session: {user_id}", extra={"user_id": user_id})
            
            # 캐시된 user 객체가 있으면 사용
            if "user" in st.session_state and st.session_state.user:
                # user_id가 일치하는지 확인
                if hasattr(st.session_state.user, 'id') and st.session_state.user.id == user_id:
                    logger.debug("Using cached user object")
                    return st.session_state.user
                else:
                    logger.debug("Cached user ID mismatch, reloading from DB")
            
            # user 객체가 없거나 불일치하면 DB에서 조회
            try:
                from src.utils.async_helpers import run_async
                logger.debug(f"Loading user from DB: user_id={user_id}")
                user = run_async(self.user_service.get_user(user_id))
                if user:
                    # 세션 상태에 캐시
                    st.session_state.user = user
                    logger.debug(f"User loaded successfully: {user.email}")
                    return user
                else:
                    logger.warning(f"User not found in DB: user_id={user_id}")
                    # 유효하지 않은 user_id면 제거
                    if "user_id" in st.session_state:
                        del st.session_state.user_id
                    if "user" in st.session_state:
                        del st.session_state.user
                    return None
            except Exception as e:
                logger.warning(f"Failed to load user from DB: {e}", exc_info=True)
                # DB 조회 실패는 일시적일 수 있으므로 user_id는 유지
                # 단, user 객체만 제거
                if "user" in st.session_state:
                    del st.session_state.user
                return None
        
        # 기존 user 객체가 있으면 반환 (하위 호환성)
        if "user" in st.session_state:
            logger.debug("Using existing user object from session")
            return st.session_state.user
        
        logger.debug("No user found in session")
        return None
    
    def is_authenticated(self) -> bool:
        """
        사용자 인증 여부 확인
        
        Returns:
            인증되어 있으면 True
        """
        return self.get_current_user() is not None
    
    def require_auth(self, redirect_to: str = "pages/login.py"):
        """
        인증이 필요한 페이지에서 사용하는 데코레이터
        
        Args:
            redirect_to: 인증되지 않은 경우 리다이렉트할 페이지
        
        Returns:
            데코레이터 함수
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                if not self.is_authenticated():
                    st.warning("로그인이 필요합니다.")
                    st.stop()
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    async def login(self, email: str, password: str) -> User:
        """
        사용자 로그인
        
        Args:
            email: 이메일 주소
            password: 비밀번호
        
        Returns:
            로그인한 User 객체
        
        Raises:
            AuthenticationError: 인증 실패 시
        """
        try:
            user = await self.user_service.authenticate(email, password)
            # user_id를 저장 (새로고침 후에도 유지)
            st.session_state.user_id = user.id
            # User 객체도 캐시 (성능 향상)
            st.session_state.user = user
            logger.info(f"User logged in: {email}", extra={"user_id": user.id})
            return user
        except Exception as e:
            logger.error(f"Login failed: {e}", extra={"email": email})
            raise AuthenticationError(f"Login failed: {str(e)}")
    
    def logout(self) -> None:
        """
        사용자 로그아웃
        """
        if "user" in st.session_state:
            user_id = st.session_state.user.id if st.session_state.user else None
            logger.info(f"User logged out: user_id={user_id}")
            del st.session_state.user
        if "user_id" in st.session_state:
            del st.session_state.user_id
    
    async def get_user_profile(self) -> Optional[User]:
        """
        현재 사용자의 프로필 조회
        
        Returns:
            User 객체 (프로필 포함) 또는 None
        """
        user = self.get_current_user()
        if not user:
            return None
        
        try:
            return await self.user_service.get_user_with_profile(user.id)
        except UserNotFoundError:
            self.logout()
            return None


# 전역 인증 미들웨어 인스턴스
auth_middleware = AuthMiddleware()

