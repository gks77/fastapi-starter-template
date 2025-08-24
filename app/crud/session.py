import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate


def get_current_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class CRUDSession:
    """CRUD operations for Session model."""

    def get(self, db: DBSession, id: uuid.UUID) -> Optional[Session]:
        """Get session by UUID."""
        return db.query(Session).filter(
            Session.id == id, 
            Session.is_deleted == False
        ).first()

    def get_by_token_hash(self, db: DBSession, *, token_hash: str) -> Optional[Session]:
        """Get session by token hash."""
        return db.query(Session).filter(
            Session.token_hash == token_hash,
            Session.is_deleted == False,
            Session.is_active == True,
            Session.expires_at > get_current_utc()
        ).first()

    def get_by_refresh_token_hash(self, db: DBSession, *, refresh_token_hash: str) -> Optional[Session]:
        """Get session by refresh token hash."""
        return db.query(Session).filter(
            Session.refresh_token_hash == refresh_token_hash,
            Session.is_deleted == False,
            Session.is_active == True,
            Session.expires_at > get_current_utc()
        ).first()

    def get_user_sessions(
        self, 
        db: DBSession, 
        *, 
        user_id: uuid.UUID, 
        active_only: bool = True,
        include_expired: bool = False
    ) -> List[Session]:
        """Get all sessions for a user."""
        query = db.query(Session).filter(
            Session.user_id == user_id,
            Session.is_deleted == False
        )
        
        if active_only:
            query = query.filter(Session.is_active == True)
        
        if not include_expired:
            query = query.filter(Session.expires_at > get_current_utc())
        
        return query.order_by(Session.last_activity.desc()).all()

    def get_active_sessions_count(self, db: DBSession, *, user_id: uuid.UUID) -> int:
        """Get count of active sessions for a user."""
        return db.query(Session).filter(
            Session.user_id == user_id,
            Session.is_deleted == False,
            Session.is_active == True,
            Session.expires_at > get_current_utc()
        ).count()

    def create(self, db: DBSession, *, obj_in: SessionCreate) -> Session:
        """Create new session."""
        db_obj = Session(
            user_id=obj_in.user_id,
            token_hash=obj_in.token_hash,
            refresh_token_hash=obj_in.refresh_token_hash,
            expires_at=obj_in.expires_at,
            is_active=obj_in.is_active,
            device_info=obj_in.device_info,
            ip_address=obj_in.ip_address,
            other_details=obj_in.other_details or {},
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: DBSession,
        *,
        db_obj: Session,
        obj_in: SessionUpdate
    ) -> Session:
        """Update session."""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_last_activity(self, db: DBSession, *, session: Session) -> Session:
        """Update session's last activity timestamp."""
        session.last_activity = get_current_utc()
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def deactivate_session(self, db: DBSession, *, session_id: uuid.UUID) -> Optional[Session]:
        """Deactivate a specific session."""
        session = self.get(db, id=session_id)
        if session:
            session.is_active = False
            db.add(session)
            db.commit()
            db.refresh(session)
        return session

    def deactivate_user_sessions(
        self, 
        db: DBSession, 
        *, 
        user_id: uuid.UUID, 
        exclude_session_id: Optional[uuid.UUID] = None
    ) -> int:
        """Deactivate all sessions for a user, optionally excluding one session."""
        query = db.query(Session).filter(
            Session.user_id == user_id,
            Session.is_deleted == False,
            Session.is_active == True
        )
        
        if exclude_session_id:
            query = query.filter(Session.id != exclude_session_id)
        
        count = query.count()
        query.update({"is_active": False})
        db.commit()
        return count

    def cleanup_expired_sessions(self, db: DBSession) -> int:
        """Clean up expired sessions (soft delete)."""
        expired_sessions = db.query(Session).filter(
            Session.expires_at <= get_current_utc(),
            Session.is_deleted == False
        )
        
        count = expired_sessions.count()
        expired_sessions.update({"is_deleted": True})
        db.commit()
        return count

    def remove(self, db: DBSession, *, id: uuid.UUID, soft_delete: bool = True) -> Optional[Session]:
        """Remove session by UUID (soft delete by default)."""
        obj = db.query(Session).filter(Session.id == id).first()
        if obj:
            if soft_delete:
                obj.is_deleted = True
                db.add(obj)
            else:
                db.delete(obj)
            db.commit()
        return obj


session = CRUDSession()
