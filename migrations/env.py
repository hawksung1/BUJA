"""
Alembic 마이그레이션 환경 설정
"""
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 설정 모듈 import
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from config.database import db

# Alembic Config 객체
config = context.config

# 데이터베이스 URL 설정 (Alembic은 동기식 URL 필요)
# asyncpg, aiosqlite 등의 비동기 드라이버 접두사 제거
db_url = settings.database_url
# 비동기 드라이버 접두사 제거
for prefix in ["+asyncpg", "+aiosqlite", "+asyncmy", "+aiomysql"]:
    db_url = db_url.replace(prefix, "")
config.set_main_option("sqlalchemy.url", db_url)

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 메타데이터 import
from src.models import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인 마이그레이션 실행"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """마이그레이션 실행"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """온라인 마이그레이션 실행 (비동기)"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())

