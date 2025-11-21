"""
보안 관련 유틸리티
"""
import bcrypt

from config.logging import get_logger
from config.settings import settings

logger = get_logger(__name__)


def hash_password(password: str) -> str:
    """
    비밀번호 해싱 (bcrypt)
    
    Args:
        password: 평문 비밀번호
    
    Returns:
        해시된 비밀번호
    """
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증
    
    Args:
        password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
    
    Returns:
        비밀번호가 일치하면 True, 아니면 False
    """
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False

