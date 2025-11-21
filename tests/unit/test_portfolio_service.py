"""
PortfolioService 단위 테스트
"""
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.database import Database
from src.models import InvestmentRecord
from src.services.portfolio_service import PortfolioService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def portfolio_service(mock_db):
    """PortfolioService 인스턴스"""
    return PortfolioService(database=mock_db)


class TestPortfolioService:
    """PortfolioService 테스트"""

    @pytest.mark.asyncio
    async def test_analyze_portfolio(self, portfolio_service, mock_db):
        """포트폴리오 분석 테스트"""
        records = [
            InvestmentRecord(
                id=1, user_id=1, asset_type="STOCK", symbol="AAPL",
                quantity=Decimal("10"), buy_price=Decimal("100"),
                buy_date=date(2024, 1, 1), realized=False
            )
        ]

        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        portfolio_service.user_service = mock_user_service

        mock_record_repo = MagicMock()
        mock_record_repo.get_unrealized = AsyncMock(return_value=records)
        portfolio_service.record_repo = mock_record_repo

        mock_analysis_repo = MagicMock()
        mock_analysis_repo.create = AsyncMock()
        portfolio_service.analysis_repo = mock_analysis_repo

        mock_session = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await portfolio_service.analyze_portfolio(1)

        assert "portfolio" in result
        assert "performance" in result
        assert "risk" in result
        assert result["portfolio"]["total_value"] > 0

    @pytest.mark.asyncio
    async def test_get_current_allocation(self, portfolio_service):
        """현재 자산 배분 조회 테스트"""
        records = [
            InvestmentRecord(
                id=1, user_id=1, asset_type="STOCK",
                quantity=Decimal("10"), buy_price=Decimal("100"),
                buy_date=date(2024, 1, 1), realized=False
            ),
            InvestmentRecord(
                id=2, user_id=1, asset_type="BOND",
                quantity=Decimal("5"), buy_price=Decimal("200"),
                buy_date=date(2024, 1, 1), realized=False
            )
        ]

        mock_record_repo = MagicMock()
        mock_record_repo.get_unrealized = AsyncMock(return_value=records)
        portfolio_service.record_repo = mock_record_repo

        allocation = await portfolio_service.get_current_allocation(1)

        assert "STOCK" in allocation
        assert "BOND" in allocation
        assert sum(allocation.values()) == pytest.approx(100.0, rel=0.01)

