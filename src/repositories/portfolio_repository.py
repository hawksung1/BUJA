"""
Portfolio Repository 구현
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import Database
from config.logging import get_logger
from src.models.portfolio import (
    AssetRecommendation,
    PortfolioAnalysis,
    RebalancingHistory,
    Screenshot,
)
from src.repositories.base_repository import BaseRepository

logger = get_logger(__name__)


class ScreenshotRepository(BaseRepository[Screenshot]):
    """Screenshot Repository"""

    def __init__(self, db: Database):
        super().__init__(db, Screenshot)

    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        session: Optional[AsyncSession] = None
    ) -> List[Screenshot]:
        """
        사용자 ID로 스크린샷 목록 조회
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 최대 조회 레코드 수
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            Screenshot 리스트
        """
        query = (
            select(Screenshot)
            .where(Screenshot.user_id == user_id)
            .where(Screenshot.deleted_at.is_(None))
            .order_by(Screenshot.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        if session:
            result = await session.execute(query)
            return list(result.scalars().all())

        async with self.db.session() as session:
            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_by_status(
        self,
        user_id: int,
        status: str,
        session: Optional[AsyncSession] = None
    ) -> List[Screenshot]:
        """
        상태별 스크린샷 조회
        
        Args:
            user_id: 사용자 ID
            status: 분석 상태 (PENDING, PROCESSING, COMPLETED, FAILED)
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            Screenshot 리스트
        """
        query = (
            select(Screenshot)
            .where(Screenshot.user_id == user_id)
            .where(Screenshot.analysis_status == status)
            .where(Screenshot.deleted_at.is_(None))
            .order_by(Screenshot.created_at.desc())
        )

        if session:
            result = await session.execute(query)
            return list(result.scalars().all())

        async with self.db.session() as session:
            result = await session.execute(query)
            return list(result.scalars().all())


class PortfolioAnalysisRepository(BaseRepository[PortfolioAnalysis]):
    """PortfolioAnalysis Repository"""

    def __init__(self, db: Database):
        super().__init__(db, PortfolioAnalysis)

    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        session: Optional[AsyncSession] = None
    ) -> List[PortfolioAnalysis]:
        """
        사용자 ID로 포트폴리오 분석 목록 조회
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 최대 조회 레코드 수
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            PortfolioAnalysis 리스트
        """
        query = (
            select(PortfolioAnalysis)
            .where(PortfolioAnalysis.user_id == user_id)
            .order_by(PortfolioAnalysis.analysis_date.desc())
            .offset(skip)
            .limit(limit)
        )

        if session:
            result = await session.execute(query)
            return list(result.scalars().all())

        async with self.db.session() as session:
            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_latest(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[PortfolioAnalysis]:
        """
        최신 포트폴리오 분석 조회
        
        Args:
            user_id: 사용자 ID
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            PortfolioAnalysis 또는 None
        """
        query = (
            select(PortfolioAnalysis)
            .where(PortfolioAnalysis.user_id == user_id)
            .order_by(PortfolioAnalysis.analysis_date.desc())
            .limit(1)
        )

        if session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()


class AssetRecommendationRepository(BaseRepository[AssetRecommendation]):
    """AssetRecommendation Repository"""

    def __init__(self, db: Database):
        super().__init__(db, AssetRecommendation)

    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        session: Optional[AsyncSession] = None
    ) -> List[AssetRecommendation]:
        """
        사용자 ID로 추천 목록 조회
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 최대 조회 레코드 수
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            AssetRecommendation 리스트
        """
        query = (
            select(AssetRecommendation)
            .where(AssetRecommendation.user_id == user_id)
            .order_by(AssetRecommendation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        if session:
            result = await session.execute(query)
            return list(result.scalars().all())

        async with self.db.session() as session:
            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_latest(
        self,
        user_id: int,
        recommendation_type: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> Optional[AssetRecommendation]:
        """
        최신 추천 조회
        
        Args:
            user_id: 사용자 ID
            recommendation_type: 추천 타입 (선택사항)
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            AssetRecommendation 또는 None
        """
        query = (
            select(AssetRecommendation)
            .where(AssetRecommendation.user_id == user_id)
        )

        if recommendation_type:
            query = query.where(AssetRecommendation.recommendation_type == recommendation_type)

        query = query.order_by(AssetRecommendation.created_at.desc()).limit(1)

        if session:
            result = await session.execute(query)
            return result.scalar_one_or_none()

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()


class RebalancingHistoryRepository(BaseRepository[RebalancingHistory]):
    """RebalancingHistory Repository"""

    def __init__(self, db: Database):
        super().__init__(db, RebalancingHistory)

    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        session: Optional[AsyncSession] = None
    ) -> List[RebalancingHistory]:
        """
        사용자 ID로 리밸런싱 이력 조회
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 최대 조회 레코드 수
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            RebalancingHistory 리스트
        """
        query = (
            select(RebalancingHistory)
            .where(RebalancingHistory.user_id == user_id)
            .order_by(RebalancingHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        if session:
            result = await session.execute(query)
            return list(result.scalars().all())

        async with self.db.session() as session:
            result = await session.execute(query)
            return list(result.scalars().all())

