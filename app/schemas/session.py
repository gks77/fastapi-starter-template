import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema


class SessionBase(BaseModel):
    """Base session schema with core session fields."""
    user_id: uuid.UUID
    expires_at: datetime
    is_active: Optional[bool] = True
    device_info: Optional[str] = None
    ip_address: Optional[str] = None


class SessionCreate(SessionBase, BaseCreateSchema):
    """Schema for creating a session."""
    token_hash: str
    refresh_token_hash: Optional[str] = None


class SessionUpdate(BaseUpdateSchema):
    """Schema for updating a session."""
    is_active: Optional[bool] = None
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    last_activity: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class Session(SessionBase, BaseSchema):
    """Schema for session response with all base fields."""
    token_hash: str
    refresh_token_hash: Optional[str] = None
    last_activity: datetime


class SessionInDB(Session):
    """Schema for session in database - same as Session for now."""
    pass


# Session management schemas
class SessionInfo(BaseModel):
    """Schema for session information without sensitive data."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_date: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    is_current: bool = Field(default=False, description="Whether this is the current session")


class ActiveSessions(BaseModel):
    """Schema for listing user's active sessions."""
    sessions: list[SessionInfo]
    total_count: int
    active_count: int
