"""
Chat Message Repository 구현
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from config.database import Database
from src.models.chat import ChatMessage
from src.repositories.base_repository import BaseRepository


class ChatMessageRepository(BaseRepository):
    """Chat Message Repository"""
    
    def __init__(self, db: Database):
        super().__init__(db, ChatMessage)
    
    async def get_by_user_id(
        self,
        user_id: int,
        limit: Optional[int] = None,
        project_id: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> List[ChatMessage]:
        """사용자 ID로 채팅 메시지 조회 (최신순)"""
        query = select(ChatMessage).where(
            ChatMessage.user_id == user_id
        )
        
        # 프로젝트 필터링
        if project_id is not None:
            query = query.where(ChatMessage.project_id == project_id)
        
        query = query.order_by(desc(ChatMessage.created_at))
        
        if limit:
            query = query.limit(limit)
        
        if session:
            result = await session.execute(query)
            return list(result.scalars().all())
        else:
            async with self.db.session() as session:
                result = await session.execute(query)
                return list(result.scalars().all())
    
    async def create_message(
        self,
        user_id: int,
        role: str,
        content: str,
        image_data: Optional[str] = None,
        image_caption: Optional[str] = None,
        project_id: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> ChatMessage:
        """채팅 메시지 생성"""
        from config.logging import get_logger
        logger = get_logger(__name__)
        
        message = ChatMessage(
            user_id=user_id,
            role=role,
            content=content,
            image_data=image_data,
            image_caption=image_caption,
            project_id=project_id
        )
        
        if session:
            session.add(message)
            await session.flush()
            await session.refresh(message)
            logger.info(f"Chat message created (with session): id={message.id}, user_id={user_id}, role={role}")
            return message
        else:
            async with self.db.session() as session:
                session.add(message)
                await session.flush()  # commit은 컨텍스트 매니저가 자동으로 처리
                await session.refresh(message)
                logger.info(f"Chat message created (new session): id={message.id}, user_id={user_id}, role={role}, content_length={len(content)}")
                return message
    
    async def delete_by_user_id(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> int:
        """사용자의 모든 채팅 메시지 삭제"""
        query = select(ChatMessage).where(ChatMessage.user_id == user_id)
        
        if session:
            result = await session.execute(query)
            messages = list(result.scalars().all())
            count = len(messages)
            for message in messages:
                await session.delete(message)
            await session.flush()
            return count
        else:
            async with self.db.session() as session:
                result = await session.execute(query)
                messages = list(result.scalars().all())
                count = len(messages)
                for message in messages:
                    await session.delete(message)
                # commit은 컨텍스트 매니저가 자동으로 처리
                return count

