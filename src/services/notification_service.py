"""
알림 서비스 - 이메일 중심, 확장 가능한 구조
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from config.database import db
from config.logging import get_logger
from src.models.notification import Notification, NotificationStatus, NotificationType
from src.repositories.notification_repository import NotificationRepository

logger = get_logger(__name__)


class NotificationService:
    """알림 서비스 - 이메일 중심, 추후 카카오톡 등 확장 가능"""
    
    def __init__(self):
        self.repo = NotificationRepository(db)
        # 이메일 서비스는 나중에 초기화 (순환 참조 방지)
        self._email_service = None
    
    @property
    def email_service(self):
        """이메일 서비스 지연 로딩"""
        if self._email_service is None:
            from src.services.email_notification_service import EmailNotificationService
            self._email_service = EmailNotificationService()
        return self._email_service
    
    async def create_notification(
        self,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        send_email: bool = True
    ) -> Notification:
        """
        알림 생성 및 전송
        
        Args:
            user_id: 사용자 ID
            type: 알림 유형
            title: 알림 제목
            message: 알림 메시지
            metadata: 추가 메타데이터 (선택)
            send_email: 이메일 전송 여부 (기본: True)
        
        Returns:
            생성된 알림
        """
        # 알림 저장
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            status=NotificationStatus.UNREAD,
            meta_data=json.dumps(metadata) if metadata else None
        )
        
        notification = await self.repo.create(notification)
        
        # 이메일 전송 (선택)
        if send_email:
            try:
                await self._send_email_notification(user_id, notification)
            except Exception as e:
                logger.warning(f"Failed to send email notification: {e}", exc_info=True)
                # 이메일 전송 실패해도 알림은 저장됨
        
        # 추후 확장: 카카오톡, SMS 등
        # await self._send_kakao_notification(user_id, notification)  # 추후 구현
        # await self._send_sms_notification(user_id, notification)     # 추후 구현
        
        logger.info(f"Notification created: id={notification.id}, type={type}, user_id={user_id}")
        return notification
    
    async def _send_email_notification(
        self,
        user_id: int,
        notification: Notification
    ):
        """이메일 알림 전송"""
        await self.email_service.send_notification_email(
            user_id=user_id,
            notification=notification
        )
    
    # 추후 확장을 위한 메서드들 (현재는 구현 안 함)
    async def _send_kakao_notification(
        self,
        user_id: int,
        notification: Notification
    ):
        """카카오톡 알림 전송 (추후 구현)"""
        # from src.services.kakao_notification_service import KakaoNotificationService
        # kakao_service = KakaoNotificationService()
        # await kakao_service.send_notification(...)
        pass
    
    async def _send_sms_notification(
        self,
        user_id: int,
        notification: Notification
    ):
        """SMS 알림 전송 (추후 구현)"""
        # from src.services.sms_notification_service import SmsNotificationService
        # sms_service = SmsNotificationService()
        # await sms_service.send_notification(...)
        pass
    
    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """사용자 알림 조회"""
        return await self.repo.get_by_user_id(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit
        )
    
    async def get_unread_count(self, user_id: int) -> int:
        """읽지 않은 알림 개수"""
        return await self.repo.get_unread_count(user_id)
    
    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """알림 읽음 처리"""
        return await self.repo.mark_as_read(notification_id, user_id)
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """모든 알림 읽음 처리"""
        return await self.repo.mark_all_as_read(user_id)
    
    async def delete(self, notification_id: int, user_id: int) -> bool:
        """알림 삭제"""
        notification = await self.repo.get_by_id(notification_id)
        if notification and notification.user_id == user_id:
            await self.repo.delete(notification_id)
            return True
        return False

