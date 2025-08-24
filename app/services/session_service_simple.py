import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from fastapi import HTTPException, status

from app.models.session import Session
from app.schemas.session import SessionCreate
from app.crud.session import session as session_crud
from app.crud.user import user as user_crud


class SessionService:
    """Service for managing user sessions."""
    
    @staticmethod
    def create_token_hash(token: str) -> str:
        """Create hash of a token for secure storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def create_session(
        self, 
        db: DBSession, 
        *,
        user_id: uuid.UUID,
        access_token: str,
        refresh_token: str,
        expires_in: int = 86400,  # 24 hours default
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        other_details: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new session for a user."""
        
        # Check if user exists
        user = user_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create token hashes
        token_hash = self.create_token_hash(access_token)
        refresh_token_hash = self.create_token_hash(refresh_token)
        
        # Calculate expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        # Create session
        session_create = SessionCreate(
            user_id=user_id,
            token_hash=token_hash,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            is_active=True,
            device_info=device_info,
            ip_address=ip_address,
            other_details=other_details or {}
        )
        
        return session_crud.create(db, obj_in=session_create)
    
    def validate_session(
        self, 
        db: DBSession, 
        *, 
        access_token: str
    ) -> Optional[Session]:
        """Validate an access token and return the session if valid."""
        token_hash = self.create_token_hash(access_token)
        return session_crud.get_by_token_hash(db, token_hash=token_hash)
    
    def revoke_session(
        self, 
        db: DBSession, 
        *, 
        session_id: uuid.UUID
    ) -> bool:
        """Revoke (deactivate) a specific session."""
        session = session_crud.deactivate_session(db, session_id=session_id)
        return session is not None
    
    def revoke_all_user_sessions(
        self, 
        db: DBSession, 
        *, 
        user_id: uuid.UUID,
        exclude_session_id: Optional[uuid.UUID] = None
    ) -> int:
        """Revoke all sessions for a user, optionally excluding one."""
        return session_crud.deactivate_user_sessions(
            db, 
            user_id=user_id, 
            exclude_session_id=exclude_session_id
        )
    
    def cleanup_expired_sessions(self, db: DBSession) -> int:
        """Clean up expired sessions across all users."""
        return session_crud.cleanup_expired_sessions(db)


session_service = SessionService()
