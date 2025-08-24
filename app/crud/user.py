import uuid
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser:
    """CRUD operations for User model."""

    def get(self, db: Session, id: uuid.UUID) -> Optional[User]:
        """Get user by UUID."""
        return db.query(User).filter(User.id == id, User.is_deleted == False).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email, User.is_deleted == False).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username, User.is_deleted == False).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[User]:
        """Get multiple users with pagination."""
        query = db.query(User)
        if not include_deleted:
            query = query.filter(User.is_deleted == False)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create new user."""
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
            other_details=obj_in.other_details or {},
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update user."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: uuid.UUID, soft_delete: bool = True) -> Optional[User]:
        """Remove user by UUID (soft delete by default)."""
        obj = db.query(User).filter(User.id == id).first()
        if obj:
            if soft_delete:
                obj.is_deleted = True
                db.add(obj)
            else:
                db.delete(obj)
            db.commit()
        return obj

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return bool(user.is_active)

    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser."""
        return bool(user.is_superuser)


user = CRUDUser()
