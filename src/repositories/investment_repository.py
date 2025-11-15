"""
Investment Repository 구현
"""
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from config.database import Database
from src.models.investment import InvestmentPreference, InvestmentRecord
from src.models.financial import FinancialSituation, FinancialGoal
from src.repositories.base_repository import BaseRepository
from config.logging import get_logger

logger = get_logger(__name__)


class InvestmentPreferenceRepository(BaseRepository):
    """InvestmentPreference Repository"""
    
    def __init__(self, db: Database):
        super().__init__(db, InvestmentPreference)
    
    async def get_by_user_id(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[InvestmentPreference]:
        """
        사용자 ID로 투자 성향 조회
        
        Args:
            user_id: 사용자 ID
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            InvestmentPreference 또는 None
        """
        query = select(InvestmentPreference).where(InvestmentPreference.user_id == user_id)
        
        async def _get_by_user_id(sess: AsyncSession) -> Optional[InvestmentPreference]:
            result = await sess.execute(query)
            return result.scalar_one_or_none()
        
        return await self._execute_with_session(_get_by_user_id, session)


class InvestmentRecordRepository(BaseRepository):
    """InvestmentRecord Repository"""
    
    def __init__(self, db: Database):
        super().__init__(db, InvestmentRecord)
    
    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        session: Optional[AsyncSession] = None
    ) -> List[InvestmentRecord]:
        """
        사용자 ID로 투자 기록 목록 조회
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 최대 조회 레코드 수
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            InvestmentRecord 리스트
        """
        query = (
            select(InvestmentRecord)
            .where(InvestmentRecord.user_id == user_id)
            .order_by(InvestmentRecord.buy_date.desc())
            .offset(skip)
            .limit(limit)
        )
        
        async def _get_by_user_id(sess: AsyncSession) -> List[InvestmentRecord]:
            result = await sess.execute(query)
            return list(result.scalars().all())
        
        return await self._execute_with_session(_get_by_user_id, session)
    
    async def get_by_asset_type(
        self,
        user_id: int,
        asset_type: str,
        session: Optional[AsyncSession] = None
    ) -> List[InvestmentRecord]:
        """
        자산 유형별 투자 기록 조회
        
        Args:
            user_id: 사용자 ID
            asset_type: 자산 유형 (STOCK, BOND, FUND, etc.)
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            InvestmentRecord 리스트
        """
        query = (
            select(InvestmentRecord)
            .where(InvestmentRecord.user_id == user_id)
            .where(InvestmentRecord.asset_type == asset_type)
            .order_by(InvestmentRecord.buy_date.desc())
        )
        
        async def _get_by_asset_type(sess: AsyncSession) -> List[InvestmentRecord]:
            result = await sess.execute(query)
            return list(result.scalars().all())
        
        return await self._execute_with_session(_get_by_asset_type, session)
    
    async def get_realized(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> List[InvestmentRecord]:
        """
        실현된 투자 기록 조회
        
        Args:
            user_id: 사용자 ID
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            InvestmentRecord 리스트
        """
        query = (
            select(InvestmentRecord)
            .where(InvestmentRecord.user_id == user_id)
            .where(InvestmentRecord.realized == True)
            .order_by(InvestmentRecord.sell_date.desc())
        )
        
        async def _get_realized(sess: AsyncSession) -> List[InvestmentRecord]:
            result = await sess.execute(query)
            return list(result.scalars().all())
        
        return await self._execute_with_session(_get_realized, session)
    
    async def get_unrealized(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> List[InvestmentRecord]:
        """
        미실현 투자 기록 조회
        
        Args:
            user_id: 사용자 ID
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            InvestmentRecord 리스트
        """
        query = (
            select(InvestmentRecord)
            .where(InvestmentRecord.user_id == user_id)
            .where(InvestmentRecord.realized == False)
            .order_by(InvestmentRecord.buy_date.desc())
        )
        
        async def _get_unrealized(sess: AsyncSession) -> List[InvestmentRecord]:
            result = await sess.execute(query)
            return list(result.scalars().all())
        
        return await self._execute_with_session(_get_unrealized, session)
    
    async def get_total_investment_value(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Decimal:
        """
        총 투자 가치 계산 (미실현 기준)
        
        Args:
            user_id: 사용자 ID
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            총 투자 가치
        """
        query = (
            select(func.sum(InvestmentRecord.quantity * InvestmentRecord.buy_price))
            .where(InvestmentRecord.user_id == user_id)
            .where(InvestmentRecord.realized == False)
        )
        
        async def _get_total_value(sess: AsyncSession) -> Decimal:
            result = await sess.execute(query)
            value = result.scalar_one() or Decimal("0")
            return value
        
        return await self._execute_with_session(_get_total_value, session)


class FinancialSituationRepository(BaseRepository[FinancialSituation]):
    """FinancialSituation Repository"""
    
    def __init__(self, db: Database):
        super().__init__(db, FinancialSituation)
    
    async def get_by_user_id(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None
    ) -> Optional[FinancialSituation]:
        """
        사용자 ID로 재무 상황 조회
        
        Args:
            user_id: 사용자 ID
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            FinancialSituation 또는 None
        """
        query = select(FinancialSituation).where(FinancialSituation.user_id == user_id)
        
        async def _get_by_user_id(sess: AsyncSession) -> Optional[FinancialSituation]:
            result = await sess.execute(query)
            return result.scalar_one_or_none()
        
        return await self._execute_with_session(_get_by_user_id, session)


class FinancialGoalRepository(BaseRepository[FinancialGoal]):
    """FinancialGoal Repository"""
    
    def __init__(self, db: Database):
        super().__init__(db, FinancialGoal)
    
    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        session: Optional[AsyncSession] = None
    ) -> List[FinancialGoal]:
        """
        사용자 ID로 재무 목표 목록 조회
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 최대 조회 레코드 수
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            FinancialGoal 리스트
        """
        query = (
            select(FinancialGoal)
            .where(FinancialGoal.user_id == user_id)
            .order_by(FinancialGoal.priority.asc(), FinancialGoal.target_date.asc())
            .offset(skip)
            .limit(limit)
        )
        
        async def _get_by_user_id(sess: AsyncSession) -> List[FinancialGoal]:
            result = await sess.execute(query)
            return list(result.scalars().all())
        
        return await self._execute_with_session(_get_by_user_id, session)
    
    async def get_by_goal_type(
        self,
        user_id: int,
        goal_type: str,
        session: Optional[AsyncSession] = None
    ) -> List[FinancialGoal]:
        """
        목표 유형별 재무 목표 조회
        
        Args:
            user_id: 사용자 ID
            goal_type: 목표 유형 (RETIREMENT, HOUSE, EDUCATION, etc.)
            session: 기존 세션 (없으면 새로 생성)
            
        Returns:
            FinancialGoal 리스트
        """
        query = (
            select(FinancialGoal)
            .where(FinancialGoal.user_id == user_id)
            .where(FinancialGoal.goal_type == goal_type)
            .order_by(FinancialGoal.priority.asc())
        )
        
        async def _get_by_goal_type(sess: AsyncSession) -> List[FinancialGoal]:
            result = await sess.execute(query)
            return list(result.scalars().all())
        
        return await self._execute_with_session(_get_by_goal_type, session)

