"""
채팅 프로젝트 서비스
"""
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from config.database import Database, db
from config.logging import get_logger
from src.repositories.chat_project_repository import ChatProjectRepository

logger = get_logger(__name__)


class ChatProjectService:
    """채팅 프로젝트 관리 서비스"""

    def __init__(self, database: Optional[Database] = None):
        self.db = database or db
        self.project_repo = ChatProjectRepository(self.db)

    async def get_projects(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """사용자의 프로젝트 목록 조회"""
        projects = await self.project_repo.get_by_user_id(user_id, session)
        return [project.to_dict() for project in projects]

    async def get_project(
        self,
        project_id: int,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[Dict[str, Any]]:
        """프로젝트 조회"""
        project = await self.project_repo.get_by_id(project_id, user_id, session)
        return project.to_dict() if project else None

    async def create_project(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """프로젝트 생성"""
        project = await self.project_repo.create_project(
            user_id=user_id,
            name=name,
            description=description,
            icon=icon,
            session=session
        )
        logger.info(f"Chat project created: id={project.id}, user_id={user_id}, name={name}")
        return project.to_dict()

    async def update_project(
        self,
        project_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> Optional[Dict[str, Any]]:
        """프로젝트 업데이트"""
        project = await self.project_repo.update_project(
            project_id=project_id,
            user_id=user_id,
            name=name,
            description=description,
            icon=icon,
            session=session
        )
        if project:
            logger.info(f"Chat project updated: id={project_id}, user_id={user_id}")
            return project.to_dict()
        return None

    async def delete_project(
        self,
        project_id: int,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """프로젝트 삭제"""
        success = await self.project_repo.delete_project(project_id, user_id, session)
        if success:
            logger.info(f"Chat project deleted: id={project_id}, user_id={user_id}")
        return success

