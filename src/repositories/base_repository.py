"""
Base Repository 클래스 - 최적화된 버전
"""
from typing import Any, Awaitable, Callable, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import Database

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Repository 기본 클래스 - 간단한 CRUD 제공 (세션 관리 최적화)"""

    def __init__(self, db: Database, model: Type[T]):
        """
        Repository 초기화
        
        Args:
            db: Database 인스턴스
            model: SQLAlchemy 모델 클래스
        """
        self.db = db
        self.model = model

    async def _execute_with_session(
        self,
        operation: Callable[[AsyncSession], Awaitable[Any]],
        session: Optional[AsyncSession] = None
    ) -> Any:
        """
        세션을 사용하여 작업 실행 (중복 코드 제거)
        
        Args:
            operation: 세션을 받아 실행할 비동기 함수
            session: 기존 세션 (없으면 새로 생성)
        
        Returns:
            작업 결과
        """
        if session:
            return await operation(session)

        async with self.db.session() as session:
            return await operation(session)

    async def get_by_id(self, id: int, session: Optional[AsyncSession] = None) -> Optional[T]:
        """ID로 엔티티 조회"""
        async def _get(sess: AsyncSession) -> Optional[T]:
            return await sess.get(self.model, id)

        return await self._execute_with_session(_get, session)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        session: Optional[AsyncSession] = None
    ) -> List[T]:
        """모든 엔티티 조회 (페이징)"""
        query = select(self.model).offset(skip).limit(limit)

        async def _get_all(sess: AsyncSession) -> List[T]:
            result = await sess.execute(query)
            return list(result.scalars().all())

        return await self._execute_with_session(_get_all, session)

    async def create(self, entity: T, session: Optional[AsyncSession] = None) -> T:
        """엔티티 생성"""
        async def _create(sess: AsyncSession) -> T:
            sess.add(entity)
            await sess.flush()
            await sess.refresh(entity)
            return entity

        return await self._execute_with_session(_create, session)

    async def update(self, entity: T, session: Optional[AsyncSession] = None) -> T:
        """엔티티 업데이트"""
        async def _update(sess: AsyncSession) -> T:
            await sess.merge(entity)
            await sess.flush()
            await sess.refresh(entity)
            return entity

        return await self._execute_with_session(_update, session)

    async def delete(self, id: int, session: Optional[AsyncSession] = None) -> bool:
        """엔티티 삭제"""
        query = delete(self.model).where(self.model.id == id)

        async def _delete(sess: AsyncSession) -> bool:
            result = await sess.execute(query)
            await sess.flush()
            return result.rowcount > 0

        return await self._execute_with_session(_delete, session)

    async def delete_entity(self, entity: T, session: Optional[AsyncSession] = None) -> bool:
        """엔티티 객체로 삭제"""
        async def _delete_entity(sess: AsyncSession) -> bool:
            await sess.delete(entity)
            await sess.flush()
            return True

        return await self._execute_with_session(_delete_entity, session)

    async def count(self, session: Optional[AsyncSession] = None) -> int:
        """전체 엔티티 수 조회"""
        query = select(func.count()).select_from(self.model)

        async def _count(sess: AsyncSession) -> int:
            result = await sess.execute(query)
            return result.scalar_one()

        return await self._execute_with_session(_count, session)

    async def exists(self, id: int, session: Optional[AsyncSession] = None) -> bool:
        """엔티티 존재 여부 확인"""
        entity = await self.get_by_id(id, session)
        return entity is not None

