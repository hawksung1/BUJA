"""
글로벌 포트폴리오 필드 추가 마이그레이션 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.database import db
from sqlalchemy import text
from config.logging import get_logger

logger = get_logger(__name__)


async def add_global_portfolio_fields():
    """InvestmentPreference 테이블에 글로벌 포트폴리오 필드 추가"""
    async with db.session() as session:
        try:
            # SQLite인지 확인
            result = await session.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='investment_preferences'"))
            table_sql = result.scalar()
            
            if table_sql:
                # 이미 필드가 있는지 확인
                if 'preferred_regions' not in table_sql:
                    logger.info("Adding preferred_regions column...")
                    await session.execute(text("ALTER TABLE investment_preferences ADD COLUMN preferred_regions TEXT"))
                
                if 'currency_hedge_preference' not in table_sql:
                    logger.info("Adding currency_hedge_preference column...")
                    await session.execute(text("ALTER TABLE investment_preferences ADD COLUMN currency_hedge_preference VARCHAR(20)"))
                
                if 'home_country' not in table_sql:
                    logger.info("Adding home_country column...")
                    await session.execute(text("ALTER TABLE investment_preferences ADD COLUMN home_country VARCHAR(50)"))
                
                await session.commit()
                logger.info("글로벌 포트폴리오 필드 추가 완료")
            else:
                logger.warning("investment_preferences 테이블을 찾을 수 없습니다.")
                
        except Exception as e:
            await session.rollback()
            logger.error(f"마이그레이션 실패: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(add_global_portfolio_fields())

