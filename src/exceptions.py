"""
커스텀 예외 클래스 정의
"""
from typing import Optional


class BUJAException(Exception):
    """BUJA 프로젝트 기본 예외 클래스"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Args:
            message: 에러 메시지
            error_code: 에러 코드 (선택사항)
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


# 인증 및 사용자 관련 예외
class AuthenticationError(BUJAException):
    """인증 오류"""
    pass


class UserNotFoundError(BUJAException):
    """사용자를 찾을 수 없음"""
    pass


class UserAlreadyExistsError(BUJAException):
    """사용자가 이미 존재함"""
    pass


class InvalidCredentialsError(BUJAException):
    """잘못된 인증 정보"""
    pass


# 포트폴리오 및 투자 관련 예외
class PortfolioAnalysisError(BUJAException):
    """포트폴리오 분석 오류"""
    pass


class InvestmentRecordNotFoundError(BUJAException):
    """투자 기록을 찾을 수 없음"""
    pass


class InvalidInvestmentDataError(BUJAException):
    """잘못된 투자 데이터"""
    pass


# LLM 관련 예외
class LLMAPIError(BUJAException):
    """LLM API 호출 오류"""
    pass


class LLMProviderNotFoundError(BUJAException):
    """LLM 제공자를 찾을 수 없음"""
    pass


class LLMAPIKeyError(BUJAException):
    """LLM API 키 오류"""
    pass


# 스크린샷 분석 관련 예외
class ScreenshotAnalysisError(BUJAException):
    """스크린샷 분석 오류"""
    pass


class InvalidImageFormatError(BUJAException):
    """잘못된 이미지 형식"""
    pass


class ImageUploadError(BUJAException):
    """이미지 업로드 오류"""
    pass


# 데이터베이스 관련 예외
class DatabaseError(BUJAException):
    """데이터베이스 오류"""
    pass


class DatabaseConnectionError(BUJAException):
    """데이터베이스 연결 오류"""
    pass


# 설정 관련 예외
class ConfigurationError(BUJAException):
    """설정 오류"""
    pass


# 검증 관련 예외
class ValidationError(BUJAException):
    """데이터 검증 오류"""
    pass


# 캐시 관련 예외
class CacheError(BUJAException):
    """캐시 오류"""
    pass


# 파일 관련 예외
class FileStorageError(BUJAException):
    """파일 저장소 오류"""
    pass

