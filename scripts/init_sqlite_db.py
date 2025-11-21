"""
SQLite 데이터베이스 초기화 스크립트
마이그레이션 없이 직접 테이블 생성
"""
import asyncio

from config.database import db
from src.models import Base


async def init_database():
    """데이터베이스 테이블 생성"""
    if not db.engine:
        print("[ERROR] Database engine not initialized.")
        return

    print(f"Database URL: {db.database_url}")
    print("Creating tables...")

    try:
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[OK] Database tables created successfully!")

        # 테이블 목록 확인
        from sqlalchemy import text
        async with db.engine.connect() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = result.fetchall()
            print(f"\nCreated tables: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(init_database())

