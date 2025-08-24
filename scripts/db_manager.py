#!/usr/bin/env python3
"""
Database management utility for Fast Users API.

This script provides commands to manage database operations like
initialization, migration, and switching between databases.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base


def create_tables():
    """Create all database tables."""
    try:
        print(f"Creating tables for database: {settings.get_database_url()}")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    return True


def drop_tables():
    """Drop all database tables."""
    try:
        print(f"Dropping tables for database: {settings.get_database_url()}")
        Base.metadata.drop_all(bind=engine)
        print("✅ Tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False
    return True


def reset_database():
    """Reset database by dropping and recreating all tables."""
    print("🔄 Resetting database...")
    if drop_tables():
        return create_tables()
    return False


def init_database():
    """Initialize database with tables and initial data."""
    print("🚀 Initializing database...")
    
    # Create tables
    if not create_tables():
        return False
    
    # Run the init_db script
    try:
        from app.db.init_db import init_db
        init_db()
        print("✅ Database initialized with initial data!")
    except Exception as e:
        print(f"❌ Error initializing data: {e}")
        return False
    
    return True


def check_connection():
    """Check database connection."""
    try:
        print(f"Testing connection to: {settings.get_database_url()}")
        
        # Test connection with SQLAlchemy 2.0 syntax
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            if result:
                print("✅ Database connection successful!")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return False


def show_status():
    """Show database status and configuration."""
    print("📊 Database Status")
    print("=" * 40)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL: {settings.get_database_url()}")
    print(f"Database Type: {'PostgreSQL' if 'postgresql' in settings.get_database_url() else 'SQLite'}")
    
    if check_connection():
        try:
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Tables: {len(tables)} found")
            for table in tables:
                print(f"  - {table}")
        except Exception as e:
            print(f"❌ Error inspecting tables: {e}")


def run_migrations():
    """Run Alembic migrations."""
    try:
        print("🔄 Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✅ Migrations completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install alembic: pip install alembic")
        return False
    return True


def create_migration(message: str):
    """Create a new Alembic migration."""
    try:
        print(f"📝 Creating migration: {message}")
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)
        print("✅ Migration created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration creation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install alembic: pip install alembic")
        return False
    return True


def main():
    """Main CLI function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management utility")
    parser.add_argument("command", choices=[
        "status", "check", "init", "create", "drop", "reset", 
        "migrate", "migration"
    ], help="Command to run")
    parser.add_argument("-m", "--message", help="Migration message (for migration command)")
    
    args = parser.parse_args()
    
    if args.command == "status":
        show_status()
    elif args.command == "check":
        check_connection()
    elif args.command == "init":
        init_database()
    elif args.command == "create":
        create_tables()
    elif args.command == "drop":
        drop_tables()
    elif args.command == "reset":
        reset_database()
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "migration":
        if not args.message:
            print("❌ Migration message required. Use -m 'message'")
            sys.exit(1)
        create_migration(args.message)


if __name__ == "__main__":
    main()
