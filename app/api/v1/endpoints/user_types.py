"""
API endpoints for UserType management.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_superuser
from app.crud.user_type import user_type
from app.models.user import User
from app.schemas.user_type import UserType, UserTypeCreate, UserTypeUpdate

router = APIRouter()


@router.get("/", response_model=List[UserType])
def read_user_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> List[UserType]:
    """
    Retrieve user types. Requires superuser permissions.
    """
    user_types = user_type.get_multi(db, skip=skip, limit=limit)
    return user_types


@router.get("/active", response_model=List[UserType])
def read_active_user_types(
    db: Session = Depends(get_db),
) -> List[UserType]:
    """
    Retrieve active user types. Available to all authenticated users.
    """
    user_types = user_type.get_active(db)
    return user_types


@router.post("/", response_model=UserType)
def create_user_type(
    *,
    db: Session = Depends(get_db),
    user_type_in: UserTypeCreate,
    current_user: User = Depends(get_current_active_superuser),
) -> UserType:
    """
    Create new user type. Requires superuser permissions.
    """
    # Check if user type with same code already exists
    existing_user_type = user_type.get_by_code(db, code=user_type_in.code)
    if existing_user_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User type with this code already exists"
        )
    
    # Check if user type with same name already exists
    existing_user_type = user_type.get_by_name(db, name=user_type_in.name)
    if existing_user_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User type with this name already exists"
        )
    
    user_type_obj = user_type.create(db, obj_in=user_type_in)
    return user_type_obj


@router.put("/{user_type_id}", response_model=UserType)
def update_user_type(
    *,
    db: Session = Depends(get_db),
    user_type_id: UUID,
    user_type_in: UserTypeUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> UserType:
    """
    Update user type. Requires superuser permissions.
    """
    user_type_obj = user_type.get(db, id=user_type_id)
    if not user_type_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User type not found"
        )
    
    # Check if updating to a code that already exists (excluding current)
    if user_type_in.code:
        existing_user_type = user_type.get_by_code(db, code=user_type_in.code)
        if existing_user_type and str(existing_user_type.id) != str(user_type_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User type with this code already exists"
            )
    
    # Check if updating to a name that already exists (excluding current)
    if user_type_in.name:
        existing_user_type = user_type.get_by_name(db, name=user_type_in.name)
        if existing_user_type and str(existing_user_type.id) != str(user_type_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User type with this name already exists"
            )
    
    user_type_obj = user_type.update(db, db_obj=user_type_obj, obj_in=user_type_in)
    return user_type_obj


@router.get("/{user_type_id}", response_model=UserType)
def read_user_type(
    *,
    db: Session = Depends(get_db),
    user_type_id: UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserType:
    """
    Get user type by ID. Requires superuser permissions.
    """
    user_type_obj = user_type.get(db, id=user_type_id)
    if not user_type_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User type not found"
        )
    return user_type_obj


@router.get("/code/{code}", response_model=UserType)
def read_user_type_by_code(
    *,
    db: Session = Depends(get_db),
    code: str,
) -> UserType:
    """
    Get user type by code. Available to all authenticated users.
    """
    user_type_obj = user_type.get_by_code(db, code=code)
    if not user_type_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User type not found"
        )
    return user_type_obj


@router.delete("/{user_type_id}", response_model=UserType)
def delete_user_type(
    *,
    db: Session = Depends(get_db),
    user_type_id: UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> UserType:
    """
    Delete user type. Requires superuser permissions.
    Note: This sets is_active to False rather than actually deleting.
    """
    user_type_obj = user_type.get(db, id=user_type_id)
    if not user_type_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User type not found"
        )
    
    # Don't allow deletion of SUPER_ADMIN type
    if str(user_type_obj.code) == "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete SUPER_ADMIN user type"
        )
    
    # Soft delete by setting is_active to False
    user_type_obj = user_type.update(
        db, db_obj=user_type_obj, obj_in={"is_active": False}
    )
    return user_type_obj
