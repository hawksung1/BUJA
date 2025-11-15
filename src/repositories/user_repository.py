"""
User Repository 구현 - 단순화된 버전
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from config.database import Database
from src.models.user import User, UserProfile
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """User Repository"""
    
    def __init__(self, db: Database):
        super().__init__(db, User)
    
    async def get_by_email(
        self,
        email: str,
        session: Optional[AsyncSession] = None
    ) -> Optional[User]:
        """이메일로 사용자 조회"""
        query = select(User).where(User.email == email)
        
        if session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def get_with_profile(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[User]:
        """프로필과 함께 사용자 조회"""
        query = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.profile))
        )
        
        if session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def get_with_all_relations(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[User]:
        """모든 관계와 함께 사용자 조회"""
        query = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.financial_situation),
                selectinload(User.investment_preference),
                selectinload(User.financial_goals),
            )
        )
        
        if session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def create_user(
        self,
        email: str,
        password_hash: str,
        session: Optional[AsyncSession] = None
    ) -> User:
        """사용자 생성"""
        user = User(email=email, password_hash=password_hash)
        return await self.create(user, session)
    
    async def is_email_exists(
        self,
        email: str,
        session: Optional[AsyncSession] = None
    ) -> bool:
        """이메일 존재 여부 확인"""
        user = await self.get_by_email(email, session)
        return user is not None


class UserProfileRepository(BaseRepository):
    """UserProfile Repository"""
    
    def __init__(self, db: Database):
        super().__init__(db, UserProfile)
    
    async def get_by_user_id(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[UserProfile]:
        """사용자 ID로 프로필 조회"""
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        
        if session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

