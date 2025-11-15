"""
에러 핸들링 미들웨어
"""
from typing import Callable, Any
import traceback
from functools import wraps
from src.exceptions import BUJAException
from config.logging import get_logger

logger = get_logger(__name__)


def error_handler(func: Callable) -> Callable:
    """
    에러 핸들링 데코레이터
    
    사용 예시:
        @error_handler
        async def some_function():
            # 함수 로직
            pass
    """
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except BUJAException as e:
            # 커스텀 예외는 그대로 전파
            logger.warning(
                f"BUJA exception in {func.__name__}: {e.message}",
                extra={"error_code": e.error_code, "function": func.__name__}
            )
            raise
        except Exception as e:
            # 예상치 못한 예외는 로깅하고 래핑
            logger.error(
                f"Unexpected error in {func.__name__}: {str(e)}",
                extra={
                    "function": func.__name__,
                    "exception_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            )
            raise BUJAException(
                f"An unexpected error occurred: {str(e)}",
                error_code="INTERNAL_ERROR"
            ) from e
    
    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except BUJAException as e:
            # 커스텀 예외는 그대로 전파
            logger.warning(
                f"BUJA exception in {func.__name__}: {e.message}",
                extra={"error_code": e.error_code, "function": func.__name__}
            )
            raise
        except Exception as e:
            # 예상치 못한 예외는 로깅하고 래핑
            logger.error(
                f"Unexpected error in {func.__name__}: {str(e)}",
                extra={
                    "function": func.__name__,
                    "exception_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            )
            raise BUJAException(
                f"An unexpected error occurred: {str(e)}",
                error_code="INTERNAL_ERROR"
            ) from e
    
    # 비동기 함수인지 확인
    if hasattr(func, '__code__'):
        # 코루틴 함수인지 확인
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
    return sync_wrapper


def handle_streamlit_error(func: Callable) -> Callable:
    """
    Streamlit용 에러 핸들링 데코레이터
    
    사용 예시:
        @handle_streamlit_error
        def streamlit_page():
            # Streamlit 페이지 로직
            pass
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except BUJAException as e:
            import streamlit as st
            st.error(f"❌ {e.message}")
            logger.warning(
                f"BUJA exception in Streamlit page {func.__name__}: {e.message}",
                extra={"error_code": e.error_code}
            )
            return None
        except Exception as e:
            import streamlit as st
            logger.error(
                f"Unexpected error in Streamlit page {func.__name__}: {str(e)}",
                extra={
                    "function": func.__name__,
                    "exception_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            )
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            return None
    
    return wrapper

