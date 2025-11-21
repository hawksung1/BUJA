"""
투자 기록 관리 서비스
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional

from config.database import Database, db
from config.logging import get_logger
from src.exceptions import InvestmentRecordNotFoundError, ValidationError
from src.models import InvestmentRecord
from src.repositories import InvestmentRecordRepository
from src.services.user_service import UserService

logger = get_logger(__name__)


class InvestmentService:
    """투자 기록 관리 서비스"""

    def __init__(self, database: Optional[Database] = None):
        """
        InvestmentService 초기화
        
        Args:
            database: Database 인스턴스 (기본값: 전역 db 인스턴스)
        """
        self.db = database or db
        self.record_repo = InvestmentRecordRepository(self.db)
        self.user_service = UserService(self.db)

    async def create_investment_record(
        self,
        user_id: int,
        record_data: Dict[str, Any]
    ) -> InvestmentRecord:
        """
        투자 기록 생성
        
        Args:
            user_id: 사용자 ID
            record_data: 투자 기록 데이터
                - asset_type: 자산 유형 (STOCK, BOND, FUND, etc.)
                - symbol: 종목 코드 (선택사항)
                - quantity: 수량
                - buy_price: 매수 가격
                - buy_date: 매수 일자
                - fees: 수수료 (선택사항)
                - notes: 메모 (선택사항)
        
        Returns:
            생성된 InvestmentRecord 객체
        """
        # 사용자 존재 확인
        await self.user_service.get_user(user_id)

        # 필수 필드 검증
        required_fields = ["asset_type", "quantity", "buy_price", "buy_date"]
        for field in required_fields:
            if field not in record_data:
                raise ValidationError(f"{field} is required.")

        # 투자 기록 생성
        async with self.db.session() as session:
            record = InvestmentRecord(
                user_id=user_id,
                asset_type=record_data["asset_type"],
                symbol=record_data.get("symbol"),
                quantity=Decimal(str(record_data["quantity"])),
                buy_price=Decimal(str(record_data["buy_price"])),
                buy_date=record_data["buy_date"],
                fees=Decimal(str(record_data.get("fees", 0))),
                taxes=Decimal(str(record_data.get("taxes", 0))),
                dividend_interest=Decimal(str(record_data.get("dividend_interest", 0))),
                notes=record_data.get("notes"),
                realized=False
            )
            record = await self.record_repo.create(record, session=session)
            await session.commit()
            await session.refresh(record)

            logger.info(f"Investment record created: user_id={user_id}, record_id={record.id}")
            return record

    async def update_investment_record(
        self,
        record_id: int,
        user_id: int,
        record_data: Dict[str, Any]
    ) -> InvestmentRecord:
        """
        투자 기록 업데이트
        
        Args:
            record_id: 기록 ID
            user_id: 사용자 ID
            record_data: 업데이트할 데이터
        
        Returns:
            업데이트된 InvestmentRecord 객체
        """
        # 기록 조회 및 소유권 확인
        record = await self.record_repo.get_by_id(record_id)
        if not record:
            raise InvestmentRecordNotFoundError(f"Investment record not found: {record_id}")

        if record.user_id != user_id:
            raise ValidationError("본인의 투자 기록만 수정할 수 있습니다.")

        # 업데이트
        async with self.db.session() as session:
            if "quantity" in record_data:
                record.quantity = Decimal(str(record_data["quantity"]))
            if "buy_price" in record_data:
                record.buy_price = Decimal(str(record_data["buy_price"]))
            if "sell_price" in record_data:
                record.sell_price = Decimal(str(record_data["sell_price"]))
            if "buy_date" in record_data:
                record.buy_date = record_data["buy_date"]
            if "sell_date" in record_data:
                record.sell_date = record_data["sell_date"]
            if "fees" in record_data:
                record.fees = Decimal(str(record_data["fees"]))
            if "taxes" in record_data:
                record.taxes = Decimal(str(record_data["taxes"]))
            if "dividend_interest" in record_data:
                record.dividend_interest = Decimal(str(record_data["dividend_interest"]))
            if "notes" in record_data:
                record.notes = record_data["notes"]
            if "realized" in record_data:
                record.realized = record_data["realized"]

            # 손익 계산
            if record.sell_price and record.quantity and record.buy_price:
                profit_loss = (
                    (record.sell_price - record.buy_price) * record.quantity
                    - record.fees - record.taxes
                    + record.dividend_interest
                )
                record.profit_loss = profit_loss

            record = await self.record_repo.update(record, session=session)
            await session.commit()
            await session.refresh(record)

            logger.info(f"Investment record updated: record_id={record_id}")
            return record

    async def delete_investment_record(
        self,
        record_id: int,
        user_id: int
    ) -> bool:
        """
        투자 기록 삭제
        
        Args:
            record_id: 기록 ID
            user_id: 사용자 ID
        
        Returns:
            삭제 성공 여부
        """
        # 기록 조회 및 소유권 확인
        record = await self.record_repo.get_by_id(record_id)
        if not record:
            raise InvestmentRecordNotFoundError(f"Investment record not found: {record_id}")

        if record.user_id != user_id:
            raise ValidationError("본인의 투자 기록만 삭제할 수 있습니다.")

        # 삭제
        result = await self.record_repo.delete(record_id)

        logger.info(f"Investment record deleted: record_id={record_id}")
        return result

    async def get_investment_records(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        asset_type: Optional[str] = None,
        realized: Optional[bool] = None
    ) -> List[InvestmentRecord]:
        """
        투자 기록 조회
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 최대 조회 레코드 수
            asset_type: 자산 유형 필터 (선택사항)
            realized: 실현 여부 필터 (선택사항)
        
        Returns:
            InvestmentRecord 리스트
        """
        # 사용자 존재 확인
        await self.user_service.get_user(user_id)

        if asset_type:
            records = await self.record_repo.get_by_asset_type(user_id, asset_type)
        elif realized is True:
            records = await self.record_repo.get_realized(user_id)
        elif realized is False:
            records = await self.record_repo.get_unrealized(user_id)
        else:
            records = await self.record_repo.get_by_user_id(user_id, skip=skip, limit=limit)

        return records

    async def calculate_total_investment_value(
        self,
        user_id: int
    ) -> Decimal:
        """
        총 투자 가치 계산 (미실현 기준)
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            총 투자 가치
        """
        return await self.record_repo.get_total_investment_value(user_id)


    async def get_investment_statistics(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        투자 기록 통계
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            통계 딕셔너리
        """
        # 단일 세션에서 모든 쿼리 실행 (성능 최적화)
        async with self.db.session() as session:
            all_records = await self.record_repo.get_by_user_id(user_id, session=session)
            realized_records = await self.record_repo.get_realized(user_id, session=session)
            unrealized_records = await self.record_repo.get_unrealized(user_id, session=session)

            # 자산 유형별 통계
            asset_type_stats = {}
            for record in all_records:
                asset_type = record.asset_type
                if asset_type not in asset_type_stats:
                    asset_type_stats[asset_type] = {
                        "count": 0,
                        "total_quantity": Decimal("0"),
                        "total_value": Decimal("0")
                    }
                asset_type_stats[asset_type]["count"] += 1
                asset_type_stats[asset_type]["total_quantity"] += record.quantity
                asset_type_stats[asset_type]["total_value"] += record.quantity * record.buy_price

            # 총 투자 가치 (같은 세션 사용)
            total_value = await self.record_repo.get_total_investment_value(user_id, session=session)

            # 손익 통계 (같은 세션 사용)
            realized_profit = sum(
                (record.profit_loss or Decimal("0")) for record in realized_records
            )
            unrealized_profit = Decimal("0")  # 실제로는 현재가 조회 필요

            profit_loss_stats = {
                "realized_profit_loss": realized_profit,
                "unrealized_profit_loss": unrealized_profit,
                "total_profit_loss": realized_profit + unrealized_profit
            }

            return {
                "total_records": len(all_records),
                "realized_count": len(realized_records),
                "unrealized_count": len(unrealized_records),
                "total_investment_value": float(total_value),
                "asset_type_statistics": {
                    k: {
                        "count": v["count"],
                        "total_quantity": float(v["total_quantity"]),
                        "total_value": float(v["total_value"])
                    }
                    for k, v in asset_type_stats.items()
                },
                "profit_loss": {
                    k: float(v) for k, v in profit_loss_stats.items()
                }
            }

