import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user, get_current_superuser
from app.crud.user import user as user_crud
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user_service import user_service

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> UserSchema:
    """Create new user."""
    user = user_service.create_user(db, user_in=user_in)
    return UserSchema.model_validate(user)


@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
) -> List[UserSchema]:
    """Get users (superuser only)."""
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    return [UserSchema.model_validate(user) for user in users]


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> UserSchema:
    """Get current user."""
    return UserSchema.model_validate(current_user)


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> UserSchema:
    """Get user by UUID."""
    # Users can only access their own data unless they're superuser
    if current_user.id != user_id and not user_crud.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserSchema.model_validate(user)


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> UserSchema:
    """Update user."""
    user = user_service.update_user(
        db, current_user=current_user, user_id=user_id, user_in=user_in
    )
    return UserSchema.model_validate(user)


@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_superuser),
    hard_delete: bool = False,
) -> dict:
    """Delete user (superuser only). Default is soft delete."""
    success = user_service.delete_user(db, user_id=user_id, soft_delete=not hard_delete)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    delete_type = "permanently deleted" if hard_delete else "soft deleted"
    return {"message": f"User {delete_type} successfully"}
