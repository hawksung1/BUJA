"""
Chat Project Repository 구현
"""
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import Database
from src.models.chat_project import ChatProject
from src.repositories.base_repository import BaseRepository


class ChatProjectRepository(BaseRepository):
    """Chat Project Repository"""

    def __init__(self, db: Database):
        super().__init__(db, ChatProject)

    async def get_by_user_id(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> List[ChatProject]:
        """사용자 ID로 프로젝트 조회 (최신순)"""
        query = select(ChatProject).where(
            ChatProject.user_id == user_id
        ).order_by(desc(ChatProject.created_at))

        if session:
            result = await session.execute(query)
            return list(result.scalars().all())
        else:
            async with self.db.session() as session:
                result = await session.execute(query)
                return list(result.scalars().all())

    async def get_by_id(
        self,
        project_id: int,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[ChatProject]:
        """프로젝트 ID로 조회 (사용자 확인 포함)"""
        query = select(ChatProject).where(
            ChatProject.id == project_id,
            ChatProject.user_id == user_id
        )

        if session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
        else:
            async with self.db.session() as session:
                result = await session.execute(query)
                return result.scalar_one_or_none()

    async def create_project(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> ChatProject:
        """프로젝트 생성"""
        project = ChatProject(
            user_id=user_id,
            name=name,
            description=description,
            icon=icon
        )

        if session:
            session.add(project)
            await session.flush()
            await session.refresh(project)
            return project
        else:
            async with self.db.session() as session:
                session.add(project)
                await session.flush()
                await session.refresh(project)
                return project

    async def update_project(
        self,
        project_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> Optional[ChatProject]:
        """프로젝트 업데이트"""
        project = await self.get_by_id(project_id, user_id, session)
        if not project:
            return None

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if icon is not None:
            project.icon = icon

        if session:
            await session.flush()
            await session.refresh(project)
            return project
        else:
            async with self.db.session() as session:
                await session.merge(project)
                await session.flush()
                await session.refresh(project)
                return project

    async def delete_project(
        self,
        project_id: int,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """프로젝트 삭제"""
        project = await self.get_by_id(project_id, user_id, session)
        if not project:
            return False

        if session:
            await session.delete(project)
            await session.flush()
            return True
        else:
            async with self.db.session() as session:
                await session.delete(project)
                await session.flush()
                return True

