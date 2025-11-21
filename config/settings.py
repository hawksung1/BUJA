"""
프로젝트 설정 관리 (Pydantic Settings 사용)
환경 변수로 자동 구분 (ENVIRONMENT=development|test|production)
"""
import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """애플리케이션 설정"""

    model_config = SettingsConfigDict(
        env_file=[".env.local", ".env"],  # .env.local 우선, 없으면 .env
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # .env.local에 DATABASE_URL이 없으면 기본값(SQLite) 사용
    )

    # Environment
    environment: str = Field(default="development", description="실행 환경")
    debug: bool = Field(default=False, description="디버그 모드")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/buja.db",
        description="데이터베이스 연결 URL (기본: SQLite, Docker 불필요)"
    )
    database_pool_size: int = Field(default=10, description="데이터베이스 연결 풀 크기")
    database_max_overflow: int = Field(default=20, description="데이터베이스 최대 오버플로우")

    # LLM APIs
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API 키")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API 키")
    default_llm_provider: str = Field(default="openai", description="기본 LLM 제공자")

    # Redis (optional)
    redis_url: Optional[str] = Field(default=None, description="Redis 연결 URL")
    redis_ttl: int = Field(default=3600, description="Redis 기본 TTL (초)")

    # Security
    secret_key: str = Field(
        default="change-this-secret-key-in-production",
        description="애플리케이션 시크릿 키"
    )
    bcrypt_rounds: int = Field(default=12, description="bcrypt 해싱 라운드 수")

    # File Upload
    max_upload_size: int = Field(default=10485760, description="최대 업로드 크기 (바이트, 기본 10MB)")
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"],
        description="허용된 이미지 타입"
    )

    # Logging
    log_level: str = Field(default="INFO", description="로그 레벨")
    log_file: Optional[str] = Field(default=None, description="로그 파일 경로")

    # Auto Login (Development only)
    autologin: bool = Field(default=False, description="자동 로그인 활성화 (개발 환경용)")
    autologin_email: str = Field(default="admin", description="자동 로그인 이메일")
    autologin_password: str = Field(default="admin", description="자동 로그인 비밀번호")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """로그 레벨 검증"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()

    @field_validator("default_llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """LLM 제공자 검증"""
        valid_providers = ["openai", "anthropic", "google"]
        if v.lower() not in valid_providers:
            raise ValueError(f"default_llm_provider must be one of {valid_providers}")
        return v.lower()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """환경 검증"""
        valid_environments = ["development", "test", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"environment must be one of {valid_environments}")
        return v.lower()

    @model_validator(mode="after")
    def configure_for_environment(self):
        """환경에 따라 설정 자동 조정"""
        env = self.environment.lower()

        if env == "development":
            self.debug = True
            self.log_level = "DEBUG"
            # SQLite는 기본값 사용 (pool_size는 SQLite에서 무시됨)
            if "sqlite" not in self.database_url.lower() and self.database_pool_size == 10:
                self.database_pool_size = 5
                self.database_max_overflow = 10
        elif env == "test":
            self.debug = True
            self.log_level = "WARNING"
            if "test" not in self.database_url.lower():
                # 테스트 환경도 SQLite 사용 (더 빠름)
                self.database_url = "sqlite+aiosqlite:///./data/buja_test.db"
            # SQLite는 pool_size 무시
            if "sqlite" not in self.database_url.lower():
                self.database_pool_size = 2
                self.database_max_overflow = 5
        elif env == "production":
            self.debug = False
            self.log_level = "INFO"
            if self.database_pool_size == 10:  # 기본값인 경우에만 변경
                self.database_pool_size = 20
                self.database_max_overflow = 30
            # 프로덕션 검증
            if not self.secret_key or self.secret_key == "change-this-secret-key-in-production":
                raise ValueError("SECRET_KEY must be set in production environment")
            if not self.openai_api_key and not self.anthropic_api_key:
                raise ValueError("At least one LLM API key must be set in production environment")
            # 프로덕션에서는 autologin 비활성화
            if self.autologin:
                raise ValueError("AUTOLOGIN cannot be enabled in production environment for security reasons")

        return self


# 환경 변수로 설정 인스턴스 생성
_env = os.getenv("ENVIRONMENT", "development").lower()
settings = Settings(environment=_env)

