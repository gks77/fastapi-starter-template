#!/usr/bin/env python3
"""
Database initialization script for the FastAPI Users application.
This script creates the database tables and optionally seeds initial data.
"""

import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings
from app.core.advanced_logging import advanced_logger


def create_database_tables():
    """Create all database tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False


def verify_database_connection():
    """Verify database connection."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection verified!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def create_initial_superuser():
    """Create initial superuser if it doesn't exist."""
    try:
        from app.crud.user import user_crud
        from app.schemas.user import UserCreate
        from app.db.session import SessionLocal
        
        db = SessionLocal()
        try:
            # Check if superuser exists
            existing_user = user_crud.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
            
            if not existing_user:
                # Create superuser
                user_in = UserCreate(
                    username=settings.FIRST_SUPERUSER_USERNAME,
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_superuser=True,
                    is_active=True
                )
                
                user = user_crud.create(db, obj_in=user_in)
                print(f"✅ Superuser created: {user.email}")
            else:
                print(f"ℹ️  Superuser already exists: {existing_user.email}")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")


def main():
    """Main function to initialize the database."""
    print(f"🚀 Initializing database for {settings.PROJECT_NAME}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Database URL: {settings.get_database_url()}")
    print("-" * 50)
    
    # Step 1: Verify database connection
    if not verify_database_connection():
        print("❌ Database initialization failed!")
        return 1
    
    # Step 2: Create tables
    if not create_database_tables():
        print("❌ Database initialization failed!")
        return 1
    
    # Step 3: Create initial superuser
    try:
        asyncio.run(create_initial_superuser())
    except Exception as e:
        print(f"⚠️  Warning: Could not create superuser: {e}")
    
    print("-" * 50)
    print("✅ Database initialization completed successfully!")
    print(f"🌐 You can now start the application with: uvicorn app.main:app --reload")
    print(f"📖 API Documentation: http://localhost:8000/docs")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
