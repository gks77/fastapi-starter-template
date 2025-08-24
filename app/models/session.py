from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.db.base import BaseModel, GUID


class Session(BaseModel):
    """Session model for tracking user authentication sessions."""
    
    __tablename__ = "sessions"

    user_id = Column(GUID(), nullable=False, index=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    refresh_token_hash = Column(String, nullable=True, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    device_info = Column(Text, nullable=True)  # User agent, device type, etc.
    ip_address = Column(String, nullable=True)
    image_url = Column(String(500), nullable=True)  # Image attribute for sessions
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # The following fields are inherited from BaseModel:
    # - id (UUID, primary key)
    # - created_date (DateTime) - when session was created
    # - updated_date (DateTime) - when session was last updated
    # - other_details (JSON) - for additional session metadata
    # - is_deleted (Boolean) - for soft delete of sessions
