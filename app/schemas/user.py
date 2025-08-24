from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema


class UserBase(BaseModel):
    """Base user schema with core user fields."""
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    user_type_id: Optional[UUID] = None


class UserCreate(UserBase, BaseCreateSchema):
    """Schema for creating a user."""
    password: str


class UserUpdate(BaseUpdateSchema):
    """Schema for updating a user."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    user_type_id: Optional[UUID] = None


class User(UserBase, BaseSchema):
    """Schema for user response with all base fields."""
    pass


class UserInDB(User):
    """Schema for user in database with hashed password."""
    hashed_password: str


# Authentication schemas
class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str
