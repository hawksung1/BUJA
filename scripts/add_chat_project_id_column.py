"""
chat_messages 테이블에 project_id 컬럼 추가 마이그레이션 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from config.database import db
from config.logging import get_logger

logger = get_logger(__name__)


async def add_project_id_column():
    """chat_messages 테이블에 project_id 컬럼 추가"""
    async with db.session() as session:
        try:
            # SQLite인지 확인
            result = await session.execute(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name='chat_messages'")
            )
            table_sql = result.scalar()

            if table_sql:
                # 이미 project_id 필드가 있는지 확인
                if 'project_id' not in table_sql:
                    logger.info("Adding project_id column to chat_messages table...")
                    await session.execute(
                        text("ALTER TABLE chat_messages ADD COLUMN project_id INTEGER")
                    )
                    # 외래키 제약조건 추가 (SQLite는 ALTER TABLE에서 외래키를 직접 추가할 수 없으므로, 인덱스만 추가)
                    await session.execute(
                        text("CREATE INDEX IF NOT EXISTS ix_chat_messages_project_id ON chat_messages(project_id)")
                    )
                    await session.commit()
                    logger.info("project_id 컬럼 추가 완료")
                else:
                    logger.info("project_id 컬럼이 이미 존재합니다.")
            else:
                logger.warning("chat_messages 테이블을 찾을 수 없습니다.")

        except Exception as e:
            logger.error(f"오류 발생: {e}", exc_info=True)
            await session.rollback()
            raise


async def check_chat_projects_table():
    """chat_projects 테이블이 존재하는지 확인하고 없으면 생성"""
    async with db.session() as session:
        try:
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_projects'")
            )
            table_exists = result.scalar() is not None

            if not table_exists:
                logger.info("chat_projects 테이블이 없습니다. 모델에서 생성합니다...")
                from src.models import Base
                from src.models.chat_project import ChatProject

                async with db.engine.begin() as conn:
                    await conn.run_sync(
                        lambda sync_conn: Base.metadata.create_all(
                            bind=sync_conn,
                            tables=[ChatProject.__table__]
                        )
                    )
                logger.info("chat_projects 테이블 생성 완료")
            else:
                logger.info("chat_projects 테이블이 이미 존재합니다.")

        except Exception as e:
            logger.error(f"오류 발생: {e}", exc_info=True)
            raise


async def main():
    """메인 함수"""
    logger.info("chat_messages 테이블 마이그레이션 시작...")

    # chat_projects 테이블 확인 및 생성
    await check_chat_projects_table()

    # project_id 컬럼 추가
    await add_project_id_column()

    logger.info("마이그레이션 완료!")


if __name__ == "__main__":
    asyncio.run(main())

