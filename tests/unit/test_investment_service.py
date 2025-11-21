"""
InvestmentService 단위 테스트
"""
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from config.database import Database
from src.exceptions import InvestmentRecordNotFoundError, ValidationError
from src.models import InvestmentRecord
from src.services.investment_service import InvestmentService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def investment_service(mock_db):
    """InvestmentService 인스턴스"""
    return InvestmentService(database=mock_db)


class TestInvestmentService:
    """InvestmentService 테스트"""

    @pytest.mark.asyncio
    async def test_create_investment_record(self, investment_service, mock_db):
        """투자 기록 생성 테스트"""
        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        investment_service.user_service = mock_user_service

        mock_record_repo = MagicMock()
        mock_record_repo.create = AsyncMock(return_value=InvestmentRecord(
            id=1, user_id=1, asset_type="STOCK", quantity=Decimal("10"), buy_price=Decimal("100")
        ))
        investment_service.record_repo = mock_record_repo

        mock_session = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        record_data = {
            "asset_type": "STOCK",
            "symbol": "AAPL",
            "quantity": 10,
            "buy_price": 100.0,
            "buy_date": date(2024, 1, 1)
        }

        result = await investment_service.create_investment_record(1, record_data)

        assert result.asset_type == "STOCK"
        mock_record_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_investment_record_missing_fields(self, investment_service):
        """필수 필드 누락 시 실패 테스트"""
        with pytest.raises(ValidationError):
            await investment_service.create_investment_record(1, {
                "asset_type": "STOCK"
                # quantity, buy_price, buy_date 누락
            })

    @pytest.mark.asyncio
    async def test_get_investment_statistics(self, investment_service, mock_db):
        """투자 기록 통계 테스트"""
        records = [
            InvestmentRecord(
                id=1, user_id=1, asset_type="STOCK", quantity=Decimal("10"),
                buy_price=Decimal("100"), buy_date=date(2024, 1, 1), realized=False
            )
        ]

        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        investment_service.user_service = mock_user_service

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_user_id = AsyncMock(return_value=records)
        mock_record_repo.get_realized = AsyncMock(return_value=[])
        mock_record_repo.get_unrealized = AsyncMock(return_value=records)
        mock_record_repo.get_total_investment_value = AsyncMock(return_value=Decimal("1000"))
        investment_service.record_repo = mock_record_repo

        # 세션 컨텍스트 매니저 모킹
        mock_session = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)

        stats = await investment_service.get_investment_statistics(1)

        assert stats["total_records"] == 1
        assert "asset_type_statistics" in stats
        assert "profit_loss" in stats
        # 세션이 사용되었는지 확인
        mock_record_repo.get_by_user_id.assert_called_once()
        mock_record_repo.get_realized.assert_called_once()
        mock_record_repo.get_unrealized.assert_called_once()


class TestInvestmentServiceUpdate:
    """InvestmentService.update_investment_record 테스트"""

    @pytest.mark.asyncio
    async def test_update_investment_record_success(self, investment_service, mock_db, mock_session):
        """투자 기록 업데이트 성공 테스트"""
        # Mock 설정
        record = InvestmentRecord(
            id=1,
            user_id=1,
            asset_type="STOCK",
            symbol="AAPL",
            quantity=Decimal("10"),
            buy_price=Decimal("100"),
            buy_date=date(2024, 1, 1),
            realized=False
        )

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_id = AsyncMock(return_value=record)
        mock_record_repo.update = AsyncMock(return_value=record)
        investment_service.record_repo = mock_record_repo

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # 테스트 실행
        result = await investment_service.update_investment_record(
            record_id=1,
            user_id=1,
            record_data={"quantity": 20}
        )

        assert result.quantity == Decimal("20")
        mock_record_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_investment_record_not_found(self, investment_service):
        """존재하지 않는 투자 기록 업데이트 실패 테스트"""
        mock_record_repo = MagicMock()
        mock_record_repo.get_by_id = AsyncMock(return_value=None)
        investment_service.record_repo = mock_record_repo

        with pytest.raises(InvestmentRecordNotFoundError):
            await investment_service.update_investment_record(
                record_id=999,
                user_id=1,
                record_data={"quantity": 20}
            )

    @pytest.mark.asyncio
    async def test_update_investment_record_wrong_owner(self, investment_service):
        """다른 사용자의 투자 기록 업데이트 실패 테스트"""
        record = InvestmentRecord(
            id=1,
            user_id=2,  # 다른 사용자
            asset_type="STOCK",
            quantity=Decimal("10"),
            buy_price=Decimal("100"),
            buy_date=date(2024, 1, 1)
        )

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_id = AsyncMock(return_value=record)
        investment_service.record_repo = mock_record_repo

        with pytest.raises(ValidationError):
            await investment_service.update_investment_record(
                record_id=1,
                user_id=1,  # 다른 사용자
                record_data={"quantity": 20}
            )

    @pytest.mark.asyncio
    async def test_update_investment_record_profit_loss_calculation(
        self, investment_service, mock_db, mock_session
    ):
        """투자 기록 업데이트 시 손익 계산 테스트"""
        record = InvestmentRecord(
            id=1,
            user_id=1,
            asset_type="STOCK",
            quantity=Decimal("10"),
            buy_price=Decimal("100"),
            sell_price=None,
            buy_date=date(2024, 1, 1),
            realized=False
        )

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_id = AsyncMock(return_value=record)
        mock_record_repo.update = AsyncMock(return_value=record)
        investment_service.record_repo = mock_record_repo

        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # 테스트 실행 (매도 가격 설정)
        result = await investment_service.update_investment_record(
            record_id=1,
            user_id=1,
            record_data={
                "sell_price": 120.0,
                "realized": True
            }
        )

        assert result.realized is True
        assert result.sell_price == Decimal("120")
        # 손익이 계산되었는지 확인
        assert result.profit_loss is not None


class TestInvestmentServiceDelete:
    """InvestmentService.delete_investment_record 테스트"""

    @pytest.mark.asyncio
    async def test_delete_investment_record_success(self, investment_service):
        """투자 기록 삭제 성공 테스트"""
        record = InvestmentRecord(
            id=1,
            user_id=1,
            asset_type="STOCK",
            quantity=Decimal("10"),
            buy_price=Decimal("100"),
            buy_date=date(2024, 1, 1)
        )

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_id = AsyncMock(return_value=record)
        mock_record_repo.delete = AsyncMock(return_value=True)
        investment_service.record_repo = mock_record_repo

        result = await investment_service.delete_investment_record(1, 1)

        assert result is True
        mock_record_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_investment_record_not_found(self, investment_service):
        """존재하지 않는 투자 기록 삭제 실패 테스트"""
        mock_record_repo = MagicMock()
        mock_record_repo.get_by_id = AsyncMock(return_value=None)
        investment_service.record_repo = mock_record_repo

        with pytest.raises(InvestmentRecordNotFoundError):
            await investment_service.delete_investment_record(999, 1)

    @pytest.mark.asyncio
    async def test_delete_investment_record_wrong_owner(self, investment_service):
        """다른 사용자의 투자 기록 삭제 실패 테스트"""
        record = InvestmentRecord(
            id=1,
            user_id=2,  # 다른 사용자
            asset_type="STOCK",
            quantity=Decimal("10"),
            buy_price=Decimal("100"),
            buy_date=date(2024, 1, 1)
        )

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_id = AsyncMock(return_value=record)
        investment_service.record_repo = mock_record_repo

        with pytest.raises(ValidationError):
            await investment_service.delete_investment_record(1, 1)  # 다른 사용자


class TestInvestmentServiceGetRecords:
    """InvestmentService.get_investment_records 테스트"""

    @pytest.mark.asyncio
    async def test_get_investment_records_all(self, investment_service):
        """모든 투자 기록 조회 테스트"""
        records = [
            InvestmentRecord(
                id=1, user_id=1, asset_type="STOCK",
                quantity=Decimal("10"), buy_price=Decimal("100"),
                buy_date=date(2024, 1, 1), realized=False
            ),
            InvestmentRecord(
                id=2, user_id=1, asset_type="BOND",
                quantity=Decimal("5"), buy_price=Decimal("200"),
                buy_date=date(2024, 2, 1), realized=True
            )
        ]

        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        investment_service.user_service = mock_user_service

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_user_id = AsyncMock(return_value=records)
        investment_service.record_repo = mock_record_repo

        result = await investment_service.get_investment_records(1)

        assert len(result) == 2
        mock_record_repo.get_by_user_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_investment_records_by_asset_type(self, investment_service):
        """자산 유형별 투자 기록 조회 테스트"""
        records = [
            InvestmentRecord(
                id=1, user_id=1, asset_type="STOCK",
                quantity=Decimal("10"), buy_price=Decimal("100"),
                buy_date=date(2024, 1, 1), realized=False
            )
        ]

        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        investment_service.user_service = mock_user_service

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_asset_type = AsyncMock(return_value=records)
        investment_service.record_repo = mock_record_repo

        result = await investment_service.get_investment_records(1, asset_type="STOCK")

        assert len(result) == 1
        assert result[0].asset_type == "STOCK"
        mock_record_repo.get_by_asset_type.assert_called_once_with(1, "STOCK")

    @pytest.mark.asyncio
    async def test_get_investment_records_realized(self, investment_service):
        """실현된 투자 기록 조회 테스트"""
        records = [
            InvestmentRecord(
                id=1, user_id=1, asset_type="STOCK",
                quantity=Decimal("10"), buy_price=Decimal("100"),
                buy_date=date(2024, 1, 1), realized=True
            )
        ]

        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        investment_service.user_service = mock_user_service

        mock_record_repo = MagicMock()
        mock_record_repo.get_realized = AsyncMock(return_value=records)
        investment_service.record_repo = mock_record_repo

        result = await investment_service.get_investment_records(1, realized=True)

        assert len(result) == 1
        assert result[0].realized is True
        mock_record_repo.get_realized.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_investment_records_unrealized(self, investment_service):
        """미실현 투자 기록 조회 테스트"""
        records = [
            InvestmentRecord(
                id=1, user_id=1, asset_type="STOCK",
                quantity=Decimal("10"), buy_price=Decimal("100"),
                buy_date=date(2024, 1, 1), realized=False
            )
        ]

        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        investment_service.user_service = mock_user_service

        mock_record_repo = MagicMock()
        mock_record_repo.get_unrealized = AsyncMock(return_value=records)
        investment_service.record_repo = mock_record_repo

        result = await investment_service.get_investment_records(1, realized=False)

        assert len(result) == 1
        assert result[0].realized is False
        mock_record_repo.get_unrealized.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_investment_records_with_pagination(self, investment_service):
        """페이징을 포함한 투자 기록 조회 테스트"""
        records = [
            InvestmentRecord(
                id=i, user_id=1, asset_type="STOCK",
                quantity=Decimal("10"), buy_price=Decimal("100"),
                buy_date=date(2024, 1, 1), realized=False
            )
            for i in range(1, 6)
        ]

        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        investment_service.user_service = mock_user_service

        mock_record_repo = MagicMock()
        mock_record_repo.get_by_user_id = AsyncMock(return_value=records[:3])
        investment_service.record_repo = mock_record_repo

        result = await investment_service.get_investment_records(1, skip=0, limit=3)

        assert len(result) == 3
        mock_record_repo.get_by_user_id.assert_called_once_with(1, skip=0, limit=3)


class TestInvestmentServiceCalculateTotalValue:
    """InvestmentService.calculate_total_investment_value 테스트"""

    @pytest.mark.asyncio
    async def test_calculate_total_investment_value(self, investment_service):
        """총 투자 가치 계산 테스트"""
        mock_record_repo = MagicMock()
        mock_record_repo.get_total_investment_value = AsyncMock(return_value=Decimal("1000000"))
        investment_service.record_repo = mock_record_repo

        result = await investment_service.calculate_total_investment_value(1)

        assert result == Decimal("1000000")
        mock_record_repo.get_total_investment_value.assert_called_once_with(1)
