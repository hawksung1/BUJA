"""
Repository 단위 테스트
"""
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import (
    User,
    InvestmentRecord,
    PortfolioAnalysis,
)
from src.repositories import (
    BaseRepository,
    UserRepository,
    PortfolioAnalysisRepository,
    InvestmentRecordRepository,
)
from config.database import Database


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    db = MagicMock(spec=Database)
    return db


@pytest.fixture
def mock_session():
    """Mock AsyncSession"""
    session = AsyncMock(spec=AsyncSession)
    return session


class TestBaseRepository:
    """BaseRepository 테스트"""
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, mock_db, mock_session):
        """ID로 엔티티 조회 테스트"""
        # Mock 설정
        user = User(id=1, email="test@example.com", password_hash="hash")
        mock_session.get = AsyncMock(return_value=user)
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = BaseRepository(mock_db, User)
        result = await repo.get_by_id(1)
        
        assert result == user
        mock_session.get.assert_called_once_with(User, 1)
    
    @pytest.mark.asyncio
    async def test_create(self, mock_db, mock_session):
        """엔티티 생성 테스트"""
        # Mock 설정
        user = User(email="test@example.com", password_hash="hash")
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = BaseRepository(mock_db, User)
        result = await repo.create(user)
        
        assert result == user
        mock_session.add.assert_called_once_with(user)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(user)
    
    @pytest.mark.asyncio
    async def test_delete(self, mock_db, mock_session):
        """엔티티 삭제 테스트"""
        # Mock 설정
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = BaseRepository(mock_db, User)
        result = await repo.delete(1)
        
        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.flush.assert_called_once()


class TestUserRepository:
    """UserRepository 테스트"""
    
    @pytest.mark.asyncio
    async def test_get_by_email(self, mock_db, mock_session):
        """이메일로 사용자 조회 테스트"""
        # Mock 설정
        user = User(id=1, email="test@example.com", password_hash="hash")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=user)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = UserRepository(mock_db)
        result = await repo.get_by_email("test@example.com")
        
        assert result == user
        assert result.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_create_user(self, mock_db, mock_session):
        """사용자 생성 테스트"""
        # Mock 설정
        user = User(email="test@example.com", password_hash="hashed_password")
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = UserRepository(mock_db)
        result = await repo.create_user("test@example.com", "hashed_password")
        
        assert result.email == "test@example.com"
        assert result.password_hash == "hashed_password"
        mock_session.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_email_exists(self, mock_db, mock_session):
        """이메일 존재 여부 확인 테스트"""
        # Mock 설정 - 이메일 존재하는 경우
        user = User(id=1, email="test@example.com", password_hash="hash")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=user)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = UserRepository(mock_db)
        result = await repo.is_email_exists("test@example.com")
        
        assert result is True
        
        # 이메일이 없는 경우
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        result = await repo.is_email_exists("nonexistent@example.com")
        assert result is False


class TestInvestmentRepository:
    """InvestmentRepository 테스트"""
    
    @pytest.mark.asyncio
    async def test_get_by_user_id(self, mock_db, mock_session):
        """사용자 ID로 투자 기록 조회 테스트"""
        # Mock 설정
        records = [
            InvestmentRecord(
                id=1,
                user_id=1,
                asset_type="STOCK",
                symbol="AAPL",
                quantity=Decimal("10"),
                buy_price=Decimal("150.00"),
                buy_date=date(2024, 1, 1)
            ),
            InvestmentRecord(
                id=2,
                user_id=1,
                asset_type="BOND",
                quantity=Decimal("5"),
                buy_price=Decimal("100.00"),
                buy_date=date(2024, 2, 1)
            ),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=records)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = InvestmentRecordRepository(mock_db)
        result = await repo.get_by_user_id(1)
        
        assert len(result) == 2
        assert result[0].asset_type == "STOCK"
        assert result[1].asset_type == "BOND"
    
    @pytest.mark.asyncio
    async def test_get_unrealized(self, mock_db, mock_session):
        """미실현 투자 기록 조회 테스트"""
        # Mock 설정
        record = InvestmentRecord(
            id=1,
            user_id=1,
            asset_type="STOCK",
            symbol="AAPL",
            quantity=Decimal("10"),
            buy_price=Decimal("150.00"),
            buy_date=date(2024, 1, 1),
            realized=False
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[record])
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = InvestmentRecordRepository(mock_db)
        result = await repo.get_unrealized(1)
        
        assert len(result) == 1
        assert result[0].realized is False


class TestPortfolioRepository:
    """PortfolioRepository 테스트"""
    
    @pytest.mark.asyncio
    async def test_get_by_user_id(self, mock_db, mock_session):
        """사용자 ID로 포트폴리오 분석 조회 테스트"""
        # Mock 설정
        analysis = PortfolioAnalysis(
            id=1,
            user_id=1,
            analysis_date=date(2024, 1, 1),
            total_value=Decimal("1000000"),
            asset_allocation={"stock": 60, "bond": 30, "cash": 10}
        )
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[analysis])
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = PortfolioAnalysisRepository(mock_db)
        result = await repo.get_by_user_id(1)
        
        assert len(result) == 1
        assert result[0].user_id == 1
        assert result[0].total_value == Decimal("1000000")
    
    @pytest.mark.asyncio
    async def test_get_latest(self, mock_db, mock_session):
        """최신 포트폴리오 분석 조회 테스트"""
        # Mock 설정
        analysis = PortfolioAnalysis(
            id=1,
            user_id=1,
            analysis_date=date(2024, 1, 1),
            total_value=Decimal("1000000")
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=analysis)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Repository 생성 및 테스트
        repo = PortfolioAnalysisRepository(mock_db)
        result = await repo.get_latest(1)
        
        assert result is not None
        assert result.user_id == 1

