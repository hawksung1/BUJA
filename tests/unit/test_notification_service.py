"""
알림 서비스 테스트
"""

import pytest

from src.models.notification import NotificationStatus, NotificationType
from src.models.user import User
from src.services.notification_service import NotificationService
from src.utils.security import hash_password


@pytest.mark.asyncio
async def test_create_notification(db_session):
    """알림 생성 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_notification@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = NotificationService()

    notification = await service.create_notification(
        user_id=user.id,
        type=NotificationType.RISK_ALERT,
        title="리스크 경고",
        message="포트폴리오 리스크가 높습니다.",
        send_email=False  # 테스트에서는 이메일 전송 스킵
    )

    assert notification is not None
    assert notification.user_id == user.id
    assert notification.type == NotificationType.RISK_ALERT
    assert notification.title == "리스크 경고"
    assert notification.status == NotificationStatus.UNREAD


@pytest.mark.asyncio
async def test_get_user_notifications(db_session):
    """사용자 알림 조회 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_notifications@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = NotificationService()

    # 알림 생성
    await service.create_notification(
        user_id=user.id,
        type=NotificationType.GOAL_PROGRESS,
        title="목표 진행률",
        message="목표 진행률이 50%입니다.",
        send_email=False
    )

    # 알림 조회
    notifications = await service.get_user_notifications(user.id)

    assert len(notifications) >= 1
    assert notifications[0].type == NotificationType.GOAL_PROGRESS


@pytest.mark.asyncio
async def test_mark_as_read(db_session):
    """알림 읽음 처리 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_mark_read@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = NotificationService()

    # 알림 생성
    notification = await service.create_notification(
        user_id=user.id,
        type=NotificationType.REBALANCING_NEEDED,
        title="리밸런싱 필요",
        message="리밸런싱이 필요합니다.",
        send_email=False
    )

    assert notification.status == NotificationStatus.UNREAD

    # 읽음 처리
    result = await service.mark_as_read(notification.id, user.id)
    assert result is True

    # 다시 조회하여 확인
    updated_notification = await service.repo.get_by_id(notification.id)
    assert updated_notification.status == NotificationStatus.READ
    assert updated_notification.read_at is not None


@pytest.mark.asyncio
async def test_get_unread_count(db_session):
    """읽지 않은 알림 개수 테스트"""
    # 테스트 사용자 생성
    user = User(
        email="test_unread_count@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    service = NotificationService()

    # 알림 여러 개 생성
    for i in range(3):
        await service.create_notification(
            user_id=user.id,
            type=NotificationType.PORTFOLIO_REVIEW,
            title=f"포트폴리오 리뷰 {i+1}",
            message=f"리뷰 메시지 {i+1}",
            send_email=False
        )

    # 읽지 않은 개수 확인
    unread_count = await service.get_unread_count(user.id)
    assert unread_count >= 3

    # 하나 읽음 처리
    notifications = await service.get_user_notifications(user.id, unread_only=True)
    if notifications:
        await service.mark_as_read(notifications[0].id, user.id)

        # 다시 확인
        unread_count_after = await service.get_unread_count(user.id)
        assert unread_count_after == unread_count - 1

