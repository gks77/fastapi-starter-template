import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User


class UserService:
    """Business logic for user operations."""

    def create_user(self, db: Session, *, user_in: UserCreate) -> User:
        """Create new user with validation."""
        # Check if user with username already exists
        user_by_username = user_crud.get_by_username(db, username=user_in.username)
        if user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if user with email already exists
        user_by_email = user_crud.get_by_email(db, email=user_in.email)
        if user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        return user_crud.create(db, obj_in=user_in)

    def get_user(self, db: Session, *, user_id: uuid.UUID) -> Optional[User]:
        """Get user by UUID."""
        return user_crud.get(db, id=user_id)

    def get_user_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get user by username."""
        return user_crud.get_by_username(db, username=username)

    def get_user_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email."""
        return user_crud.get_by_email(db, email=email)

    def update_user(
        self, 
        db: Session, 
        *, 
        current_user: User, 
        user_id: uuid.UUID, 
        user_in: UserUpdate
    ) -> User:
        """Update user with permissions check."""
        # Check if user exists
        user = user_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions - users can only update themselves unless they're superuser
        if current_user.id != user_id and not user_crud.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Non-superusers cannot modify superuser status
        if (not user_crud.is_superuser(current_user) and 
            user_in.is_superuser is not None):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify superuser status"
            )
        
        # Check for username conflicts
        if user_in.username and user_in.username != user.username:
            existing_user = user_crud.get_by_username(db, username=user_in.username)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Check for email conflicts
        if user_in.email and user_in.email != user.email:
            existing_user = user_crud.get_by_email(db, email=user_in.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
        
        return user_crud.update(db, db_obj=user, obj_in=user_in)

    def delete_user(self, db: Session, *, user_id: uuid.UUID, soft_delete: bool = True) -> bool:
        """Delete user by UUID (soft delete by default)."""
        user = user_crud.get(db, id=user_id)
        if not user:
            return False
        
        user_crud.remove(db, id=user_id, soft_delete=soft_delete)
        return True

    def authenticate_user(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        return user_crud.authenticate(db, username=username, password=password)


user_service = UserService()
