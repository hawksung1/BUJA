#!/usr/bin/env python3
"""
Create default admin user (admin/admin)
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services import UserService
from src.repositories import UserRepository
from config.database import db
from config.logging import get_logger

logger = get_logger(__name__)


async def create_admin_user():
    """Create admin user if it doesn't exist"""
    user_service = UserService()
    user_repo = UserRepository(db)
    
    # Check if admin user exists
    admin_user = await user_repo.get_by_email("admin")
    
    if admin_user:
        print("✅ Admin user already exists")
        return admin_user
    
    # Create admin user
    try:
        admin_user = await user_service.register(
            email="admin",
            password="admin",
            profile_data={
                "name": "Administrator",
                "occupation": "System Admin"
            },
            skip_validation=True  # Skip validation for admin account
        )
        print("✅ Admin user created successfully!")
        print(f"   Email: admin")
        print(f"   Password: admin")
        return admin_user
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        raise


async def main():
    """Main function"""
    print("=" * 60)
    print("Creating Admin User")
    print("=" * 60)
    
    try:
        await create_admin_user()
        print("=" * 60)
        print("✅ Complete!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

