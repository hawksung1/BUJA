"""
데이터 검증 유틸리티
"""
import re

from src.exceptions import ValidationError


def validate_email(email: str) -> bool:
    """
    이메일 주소 검증
    
    Args:
        email: 이메일 주소
    
    Returns:
        유효한 이메일이면 True
    
    Raises:
        ValidationError: 이메일 형식이 잘못된 경우
    """
    if not email:
        raise ValidationError("이메일 주소는 필수입니다.")

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("유효하지 않은 이메일 형식입니다.")

    return True


def validate_password(password: str, min_length: int = 8) -> bool:
    """
    비밀번호 검증
    
    Args:
        password: 비밀번호
        min_length: 최소 길이
    
    Returns:
        유효한 비밀번호이면 True
    
    Raises:
        ValidationError: 비밀번호가 요구사항을 만족하지 않는 경우
    """
    if not password:
        raise ValidationError("비밀번호는 필수입니다.")

    if len(password) < min_length:
        raise ValidationError(f"비밀번호는 최소 {min_length}자 이상이어야 합니다.")

    # 영문, 숫자, 특수문자 중 2가지 이상 포함
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    if sum([has_letter, has_digit, has_special]) < 2:
        raise ValidationError(
            "비밀번호는 영문, 숫자, 특수문자 중 2가지 이상을 포함해야 합니다."
        )

    return True


def validate_positive_number(value: float, field_name: str = "값") -> bool:
    """
    양수 검증
    
    Args:
        value: 검증할 값
        field_name: 필드 이름 (에러 메시지용)
    
    Returns:
        양수이면 True
    
    Raises:
        ValidationError: 값이 양수가 아닌 경우
    """
    if value <= 0:
        raise ValidationError(f"{field_name}은(는) 양수여야 합니다.")
    return True


def validate_percentage(value: float, field_name: str = "값") -> bool:
    """
    퍼센트 값 검증 (0-100)
    
    Args:
        value: 검증할 값
        field_name: 필드 이름 (에러 메시지용)
    
    Returns:
        유효한 퍼센트이면 True
    
    Raises:
        ValidationError: 값이 0-100 범위가 아닌 경우
    """
    if not (0 <= value <= 100):
        raise ValidationError(f"{field_name}은(는) 0-100 사이의 값이어야 합니다.")
    return True

