"""
알림 서비스 테스트
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.database import Database
from src.models.notification import Notification, NotificationStatus, NotificationType
from src.services.notification_service import NotificationService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def notification_service(mock_db):
    """NotificationService 인스턴스"""
    service = NotificationService()
    service.repo = MagicMock()
    # Mock email service
    service._email_service = MagicMock()
    service._email_service.send_notification_email = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_create_notification(notification_service):
    """알림 생성 테스트"""
    user_id = 1
    
    # Mock notification creation
    notification = Notification(
        id=1,
        user_id=user_id,
        type=NotificationType.RISK_ALERT,
        title="리스크 경고",
        message="포트폴리오 리스크가 높습니다.",
        status=NotificationStatus.UNREAD
    )
    notification_service.repo.create = AsyncMock(return_value=notification)

    result = await notification_service.create_notification(
        user_id=user_id,
        type=NotificationType.RISK_ALERT,
        title="리스크 경고",
        message="포트폴리오 리스크가 높습니다.",
        send_email=False
    )

    assert result is not None
    assert result.user_id == user_id
    assert result.type == NotificationType.RISK_ALERT
    assert result.title == "리스크 경고"
    assert result.status == NotificationStatus.UNREAD
    notification_service.repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_notifications(notification_service):
    """사용자 알림 조회 테스트"""
    user_id = 1
    
    notifications = [
        Notification(
            id=1,
            user_id=user_id,
            type=NotificationType.GOAL_PROGRESS,
            title="목표 진행률",
            message="목표 진행률이 50%입니다.",
            status=NotificationStatus.UNREAD
        )
    ]
    notification_service.repo.get_by_user_id = AsyncMock(return_value=notifications)

    result = await notification_service.get_user_notifications(user_id)

    assert len(result) == 1
    assert result[0].type == NotificationType.GOAL_PROGRESS
    notification_service.repo.get_by_user_id.assert_called_once_with(user_id=user_id, unread_only=False, limit=50)


@pytest.mark.asyncio
async def test_mark_as_read(notification_service):
    """알림 읽음 처리 테스트"""
    user_id = 1
    notification_id = 1
    
    notification_service.repo.mark_as_read = AsyncMock(return_value=True)

    result = await notification_service.mark_as_read(notification_id, user_id)
    
    assert result is True
    notification_service.repo.mark_as_read.assert_called_once_with(notification_id, user_id)


@pytest.mark.asyncio
async def test_get_unread_count(notification_service):
    """읽지 않은 알림 개수 테스트"""
    user_id = 1
    
    notification_service.repo.get_unread_count = AsyncMock(return_value=3)

    unread_count = await notification_service.get_unread_count(user_id)
    
    assert unread_count == 3
    notification_service.repo.get_unread_count.assert_called_once_with(user_id)


