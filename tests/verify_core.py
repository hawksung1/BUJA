import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import db
from src.models import Base
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService


async def verify_core():
    print("1. Initializing Database...")
    try:
        # Initialize DB
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   ✅ Database initialized")
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        return

    print("\n2. Verifying User Service...")
    try:
        user_service = UserService(db)
        print("   ✅ User Service instantiated")

        # Test user creation
        email = "test_verify@example.com"
        password = "password123"

        # Clean up if exists
        repo = UserRepository(db)
        existing = await repo.get_by_email(email)
        if existing:
            print("   ℹ️ Test user already exists, skipping creation")
        else:
            await user_service.register(email, password, {"name": "Test User"})
            print("   ✅ User registration successful")

    except Exception as e:
        print(f"   ❌ User Service verification failed: {e}")
        return

    print("\n✨ Core functionality verification complete!")

if __name__ == "__main__":
    asyncio.run(verify_core())
