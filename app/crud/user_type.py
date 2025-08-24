"""
CRUD operations for UserType model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user_type import UserType
from app.schemas.user_type import UserTypeCreate, UserTypeUpdate


class CRUDUserType(CRUDBase[UserType, UserTypeCreate, UserTypeUpdate]):
    """CRUD operations for UserType."""

    def get_by_code(self, db: Session, *, code: str) -> Optional[UserType]:
        """Get user type by code."""
        return db.query(UserType).filter(UserType.code == code).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[UserType]:
        """Get user type by name."""
        return db.query(UserType).filter(UserType.name == name).first()

    def get_active(self, db: Session) -> List[UserType]:
        """Get all active user types."""
        return db.query(UserType).filter(UserType.is_active == True).all()

    def create_if_not_exists(self, db: Session, *, obj_in: UserTypeCreate) -> UserType:
        """Create user type if it doesn't exist, otherwise return existing."""
        existing = self.get_by_code(db, code=obj_in.code)
        if existing:
            return existing
        return self.create(db, obj_in=obj_in)

    def bulk_create_if_not_exists(self, db: Session, *, user_types: List[dict]) -> List[UserType]:
        """Bulk create user types if they don't exist."""
        created_types = []
        for user_type_data in user_types:
            user_type_create = UserTypeCreate(**user_type_data)
            user_type = self.create_if_not_exists(db, obj_in=user_type_create)
            created_types.append(user_type)
        return created_types


user_type = CRUDUserType(UserType)
