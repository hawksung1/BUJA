"""
전역 테스트 픽스처
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import db


@pytest.fixture
async def db_session():
    """
    데이터베이스 세션 픽스처

    각 테스트마다 새로운 세션을 제공하고, 테스트 후 롤백
    """
    async with db.session() as session:
        # 트랜잭션 시작
        transaction = await session.begin()
        try:
            yield session
        finally:
            # 롤백하여 테스트 데이터 정리
            await transaction.rollback()


@pytest.fixture
def create_test_user():
    """
    테스트 사용자 생성 헬퍼 함수

    Returns:
        async function that creates a test user
    """
    async def _create_user(session: AsyncSession):
        from src.models.user import User
        from src.utils.security import hash_password

        user = User(
            email=f"test_{pytest.current_test_name()}@example.com",
            password_hash=hash_password("testpass123"),
            is_active=True
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    return _create_user

