import pytest

from src.models import User


def test_user_model_creation():
    """Test basic User model creation"""
    user = User(
        id=1,
        email="test@example.com",
        password_hash="hash",
        is_active=True
    )
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.is_active is True

@pytest.mark.asyncio
async def test_async_setup():
    """Test async test execution capability"""
    assert True
