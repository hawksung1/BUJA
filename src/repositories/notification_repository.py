"""
알림 Repository
"""
from datetime import datetime
from typing import List, Optional

from config.database import db
from src.models.notification import Notification, NotificationStatus, NotificationType
from src.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """알림 Repository"""
    
    def __init__(self, database=None):
        super().__init__(database or db, Notification)

    async def get_by_user_id(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        session=None
    ) -> List[Notification]:
        """사용자 알림 조회"""
        async def _get_by_user_id(session):
            query = session.query(Notification).filter(
                Notification.user_id == user_id
            )
            
            if unread_only:
                query = query.filter(Notification.status == NotificationStatus.UNREAD)
            
            return list(query.order_by(Notification.created_at.desc()).limit(limit).all())
        
        return await self._execute_with_session(_get_by_user_id, session)
    
    async def get_unread_count(self, user_id: int, session=None) -> int:
        """읽지 않은 알림 개수"""
        async def _get_unread_count(session):
            return session.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.UNREAD
            ).count()
        
        return await self._execute_with_session(_get_unread_count, session)
    
    async def mark_as_read(self, notification_id: int, user_id: int, session=None) -> bool:
        """알림 읽음 처리"""
        async def _mark_as_read(session):
            notification = await session.get(Notification, notification_id)
            if notification and notification.user_id == user_id:
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.now()
                session.add(notification)
                return True
            return False
        
        return await self._execute_with_session(_mark_as_read, session)
    
    async def mark_all_as_read(self, user_id: int, session=None) -> int:
        """모든 알림 읽음 처리"""
        async def _mark_all_as_read(session):
            notifications = session.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.UNREAD
            ).all()
            
            count = 0
            for notification in notifications:
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.now()
                count += 1
            
            return count
        
        return await self._execute_with_session(_mark_all_as_read, session)

