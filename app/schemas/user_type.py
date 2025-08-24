"""
Pydantic schemas for UserType model.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserTypeBase(BaseModel):
    """Base UserType schema with common attributes."""
    name: str = Field(..., min_length=1, max_length=50, description="User type name")
    code: str = Field(..., min_length=1, max_length=20, description="User type code")
    description: Optional[str] = Field(None, description="User type description")
    is_active: bool = Field(True, description="Whether the user type is active")


class UserTypeCreate(UserTypeBase):
    """Schema for creating a new user type."""
    pass


class UserTypeUpdate(BaseModel):
    """Schema for updating a user type."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class UserTypeInDBBase(UserTypeBase):
    """Base schema for user types stored in database."""
    id: UUID
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True


class UserType(UserTypeInDBBase):
    """Schema for returning user type data."""
    pass


class UserTypeInDB(UserTypeInDBBase):
    """Schema for user type as stored in database."""
    pass


# Predefined user types
USER_TYPE_CODES = {
    "SUPER_ADMIN": "SUPER_ADMIN",
    "ADMIN": "ADMIN", 
    "HR": "HR",
    "EMPLOYEE": "EMPLOYEE",
    "USER": "USER"
}

USER_TYPE_DEFAULTS = [
    {
        "name": "Super Administrator",
        "code": "SUPER_ADMIN",
        "description": "Super administrator with full system access and all permissions",
        "is_active": True
    },
    {
        "name": "Administrator", 
        "code": "ADMIN",
        "description": "Administrator with elevated permissions for system management",
        "is_active": True
    },
    {
        "name": "Human Resources",
        "code": "HR", 
        "description": "HR personnel with access to employee management and HR functions",
        "is_active": True
    },
    {
        "name": "Employee",
        "code": "EMPLOYEE",
        "description": "Regular employee with access to internal systems and resources",
        "is_active": True
    },
    {
        "name": "User",
        "code": "USER",
        "description": "Standard user with basic access permissions",
        "is_active": True
    }
]
