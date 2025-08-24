from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.user_type import UserType  # Import UserType model
from app.models.profile import Profile  # Import to ensure table creation
from app.models.address import Address  # Import to ensure table creation
from app.models.session import Session as SessionModel  # Import to ensure table creation
from app.models.department import Department  # Import to ensure table creation
from app.models.category import Category  # Import to ensure table creation
from app.models.subcategory import Subcategory  # Import to ensure table creation
from app.models.product import Product  # Import to ensure table creation
from app.crud.user_type import user_type
from app.schemas.user_type import USER_TYPE_DEFAULTS
from app.core.logging import logger


def create_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


def create_default_user_types(db: Session) -> None:
    """Create default user types if they don't exist."""
    logger.info("Creating default user types...")
    user_type.bulk_create_if_not_exists(db, user_types=USER_TYPE_DEFAULTS)
    logger.info("Default user types created!")


def create_superuser(db: Session) -> None:
    """Create superuser if it doesn't exist."""
    user = db.query(User).filter(
        User.username == settings.FIRST_SUPERUSER_USERNAME,
        User.is_deleted == False
    ).first()
    
    if not user:
        # Get SUPER_ADMIN user type
        super_admin_type = user_type.get_by_code(db, code="SUPER_ADMIN")
        user_type_id = super_admin_type.id if super_admin_type else None
        
        user = User(
            username=settings.FIRST_SUPERUSER_USERNAME,
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_active=True,
            is_superuser=True,
            user_type_id=user_type_id,
            other_details={"created_by": "system", "role": "initial_admin"}
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Superuser created: {settings.FIRST_SUPERUSER_USERNAME}")
    else:
        logger.info(f"Superuser already exists: {settings.FIRST_SUPERUSER_USERNAME}")


def init_db() -> None:
    """Initialize database with tables and superuser."""
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created!")
    
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        logger.info("Creating default user types...")
        create_default_user_types(db)
        
        logger.info("Creating superuser...")
        create_superuser(db)
    finally:
        db.close()
    
    logger.info("Database initialization complete!")
