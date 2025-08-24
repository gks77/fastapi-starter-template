import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session as DBSession
from fastapi import HTTPException, status

from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate, SessionInfo, ActiveSessions
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
        max_sessions: int = 5,
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
        
        # Cleanup old sessions if max sessions exceeded
        active_sessions_count = session_crud.get_active_sessions_count(
            db, user_id=user_id
        )
        
        if active_sessions_count >= max_sessions:
            # Deactivate some old sessions to make room
            sessions_to_deactivate = active_sessions_count - max_sessions + 1
            user_sessions = session_crud.get_user_sessions(
                db, user_id=user_id, active_only=True
            )
            
            # Deactivate oldest sessions (assuming sessions are ordered by last_activity desc)
            for i in range(sessions_to_deactivate):
                if i < len(user_sessions):
                    session_crud.deactivate_session(db, session_id=user_sessions[-(i+1)].id)
        
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
        session = session_crud.get_by_token_hash(db, token_hash=token_hash)
        
        if session:
            # Update last activity
            session_crud.update_last_activity(db, session=session)
        
        return session
    
    def refresh_session(
        self, 
        db: DBSession, 
        *, 
        refresh_token: str,
        new_access_token: str,
        new_refresh_token: str,
        expires_in: int = 86400
    ) -> Optional[Session]:
        """Refresh a session with new tokens."""
        refresh_token_hash = self.create_token_hash(refresh_token)
        session = session_crud.get_by_refresh_token_hash(
            db, refresh_token_hash=refresh_token_hash
        )
        
        if not session:
            return None
        
        # Update session with new tokens using direct database update
        new_token_hash = self.create_token_hash(new_access_token)
        new_refresh_token_hash = self.create_token_hash(new_refresh_token)
        new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        # Use direct update to avoid SQLAlchemy assignment issues
        db.query(Session).filter(Session.id == session.id).update({
            "token_hash": new_token_hash,
            "refresh_token_hash": new_refresh_token_hash,
            "expires_at": new_expires_at,
            "last_activity": datetime.now(timezone.utc)
        })
        db.commit()
        db.refresh(session)
        
        return session
    
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
    
    def get_user_sessions(
        self, 
        db: DBSession, 
        *, 
        user_id: uuid.UUID,
        active_only: bool = True
    ) -> List[SessionInfo]:
        """Get all sessions for a user."""
        sessions = session_crud.get_user_sessions(
            db, user_id=user_id, active_only=active_only
        )
        
        session_infos = []
        for session in sessions:
            session_info = SessionInfo(
                id=session.id,
                user_id=session.user_id,
                device_info=session.device_info,
                ip_address=session.ip_address,
                last_activity=session.last_activity,
                created_date=session.created_date,
                is_active=session.is_active,
                expires_at=session.expires_at
            )
            session_infos.append(session_info)
        
        return session_infos
    
    def get_active_sessions_summary(
        self, 
        db: DBSession, 
        *, 
        user_id: uuid.UUID
    ) -> ActiveSessions:
        """Get summary of active sessions for a user."""
        sessions = session_crud.get_user_sessions(
            db, user_id=user_id, active_only=True
        )
        
        session_infos = []
        for session in sessions:
            session_info = SessionInfo(
                id=session.id,
                device_info=session.device_info,
                ip_address=session.ip_address,
                last_activity=session.last_activity,
                created_date=session.created_date,
                is_active=session.is_active,
                expires_at=session.expires_at
            )
            session_infos.append(session_info)
        
        return ActiveSessions(
            total_count=len(session_infos),
            sessions=session_infos
        )
    
    def cleanup_expired_sessions(self, db: DBSession) -> int:
        """Clean up expired sessions across all users."""
        return session_crud.cleanup_expired_sessions(db)
    
    def get_session_by_token(
        self, 
        db: DBSession, 
        *, 
        access_token: str
    ) -> Optional[Session]:
        """Get session by access token without updating activity."""
        token_hash = self.create_token_hash(access_token)
        return session_crud.get_by_token_hash(db, token_hash=token_hash)


session_service = SessionService()
