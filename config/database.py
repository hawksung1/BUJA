"""
데이터베이스 설정 및 연결 관리 (SQLAlchemy 비동기)
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool, QueuePool
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)


class Database:
    """데이터베이스 연결 관리 클래스"""
    
    def __init__(self, database_url: str | None = None):
        """
        데이터베이스 초기화
        
        Args:
            database_url: 데이터베이스 연결 URL (기본값: settings.database_url)
        """
        self.database_url = database_url or settings.database_url
        
        # 데이터베이스 타입 확인
        is_sqlite = "sqlite" in self.database_url.lower()
        is_postgres = "postgresql" in self.database_url.lower() or "postgres" in self.database_url.lower()
        
        # 필요한 드라이버 확인
        if is_sqlite:
            try:
                import aiosqlite
            except ImportError:
                logger.error("aiosqlite not installed. Please install: pip install aiosqlite")
                self.engine = None
                self.session_factory = None
                return
        elif is_postgres:
            try:
                import asyncpg
            except ImportError:
                logger.warning("asyncpg not installed. For PostgreSQL, please install: pip install asyncpg")
                logger.info("Or use SQLite instead: sqlite+aiosqlite:///./data/buja.db")
                self.engine = None
                self.session_factory = None
                return
        
        # SQLite용 디렉토리 생성
        if is_sqlite:
            from pathlib import Path
            db_path = self.database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite+aiosqlite://", "")
            if db_path.startswith("./"):
                db_path = db_path[2:]
            db_file = Path(db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 비동기 엔진 생성
        try:
            engine_kwargs = {
                "echo": settings.debug,  # SQL 쿼리 로깅 (디버그 모드에서만)
            }
            
            # SQLite는 pool 설정이 필요 없음
            if not is_sqlite:
                engine_kwargs.update({
                    "poolclass": QueuePool,
                    "pool_size": settings.database_pool_size,
                    "max_overflow": settings.database_max_overflow,
                    "pool_pre_ping": True,  # 연결 유효성 검사
                })
            else:
                # SQLite는 NullPool 사용 (파일 기반이므로)
                engine_kwargs["poolclass"] = NullPool
                engine_kwargs["connect_args"] = {"check_same_thread": False}
            
            self.engine = create_async_engine(self.database_url, **engine_kwargs)
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            self.engine = None
            self.session_factory = None
            return
        
        # 세션 팩토리 생성
        if self.engine:
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        else:
            self.session_factory = None
        
        db_type = "SQLite" if "sqlite" in self.database_url.lower() else "PostgreSQL"
        logger.info(f"Database engine initialized ({db_type})", extra={
            "database_url": self._mask_database_url(self.database_url),
            "database_type": db_type,
        })
    
    @staticmethod
    def _mask_database_url(url: str) -> str:
        """데이터베이스 URL에서 비밀번호 마스킹"""
        if "@" in url:
            parts = url.split("@")
            if len(parts) == 2:
                auth_part = parts[0]
                if ":" in auth_part:
                    user_pass = auth_part.split("://")[-1]
                    if ":" in user_pass:
                        user, _ = user_pass.split(":", 1)
                        return url.replace(user_pass, f"{user}:***")
        return url
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        데이터베이스 세션 컨텍스트 매니저
        
        사용 예시:
            async with db.session() as session:
                result = await session.execute(select(User))
                users = result.scalars().all()
        """
        if not self.session_factory:
            db_type = "SQLite (aiosqlite)" if "sqlite" in self.database_url.lower() else "PostgreSQL (asyncpg)"
            raise RuntimeError(f"Database not initialized. Please install the required driver: {db_type}")
        
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Database transaction failed, rolling back")
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database engine closed")


# 전역 데이터베이스 인스턴스
db = Database()

