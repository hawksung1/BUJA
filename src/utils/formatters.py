"""
포맷팅 유틸리티
"""
from typing import Optional


def format_currency(amount: float, currency: str = "KRW") -> str:
    """
    통화 형식으로 포맷팅
    
    Args:
        amount: 금액
        currency: 통화 코드 (기본값: KRW)
    
    Returns:
        포맷팅된 통화 문자열
    """
    if currency == "KRW":
        return f"{amount:,.0f}원"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    퍼센트 형식으로 포맷팅
    
    Args:
        value: 퍼센트 값 (0-100)
        decimal_places: 소수점 자릿수
    
    Returns:
        포맷팅된 퍼센트 문자열
    """
    return f"{value:.{decimal_places}f}%"


def format_number(value: float, decimal_places: int = 2) -> str:
    """
    숫자 형식으로 포맷팅 (천 단위 구분)
    
    Args:
        value: 숫자 값
        decimal_places: 소수점 자릿수
    
    Returns:
        포맷팅된 숫자 문자열
    """
    return f"{value:,.{decimal_places}f}"

