"""
데이터 변환 유틸리티 함수
"""
from typing import List, Dict, Any, Optional
from datetime import date
from decimal import Decimal
from src.models.investment import InvestmentRecord


def investment_records_to_dict(
    records: List[InvestmentRecord],
    include_dates: bool = True,
    include_sell_price: bool = False
) -> List[Dict[str, Any]]:
    """
    InvestmentRecord 리스트를 딕셔너리 리스트로 변환
    
    Args:
        records: InvestmentRecord 리스트
        include_dates: 날짜 정보 포함 여부
        include_sell_price: 매도 가격 포함 여부
    
    Returns:
        딕셔너리 리스트
    """
    return [
        {
            "asset_type": record.asset_type,
            "symbol": record.symbol,
            "quantity": float(record.quantity),
            "buy_price": float(record.buy_price),
            "realized": record.realized,
            **({"buy_date": record.buy_date.isoformat() if record.buy_date else None} if include_dates else {}),
            **({"sell_price": float(record.sell_price) if record.sell_price else None} if include_sell_price else {}),
        }
        for record in records
    ]


def safe_decimal_to_float(value: Optional[Decimal]) -> float:
    """
    Decimal 값을 안전하게 float로 변환
    
    Args:
        value: Decimal 값 또는 None
    
    Returns:
        float 값 (None인 경우 0.0)
    """
    if value is None:
        return 0.0
    return float(value)

