from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


class CRUDProfile:
    """CRUD operations for Profile model."""

    def get(self, db: Session, id: UUID) -> Optional[Profile]:
        """Get profile by UUID."""
        return db.query(Profile).filter(
            Profile.id == id, 
            Profile.is_deleted == False
        ).first()

    def get_by_user_id(self, db: Session, *, user_id: UUID) -> Optional[Profile]:
        """Get profile by user ID."""
        return db.query(Profile).filter(
            Profile.user_id == user_id,
            Profile.is_deleted == False
        ).first()

    def get_public_profiles(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get all public profiles."""
        return db.query(Profile).filter(
            Profile.is_profile_public == "public",
            Profile.is_deleted == False
        ).offset(skip).limit(limit).all()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[Profile]:
        """Get multiple profiles with pagination."""
        query = db.query(Profile)
        if not include_deleted:
            query = query.filter(Profile.is_deleted == False)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ProfileCreate) -> Profile:
        """Create new profile."""
        # Convert schema to dict and handle defaults
        profile_data = obj_in.model_dump()
        profile_data.setdefault('is_profile_public', 'private')
        profile_data.setdefault('show_email', 'false')
        profile_data.setdefault('show_phone', 'false')
        profile_data.setdefault('other_details', {})
        
        db_obj = Profile(**profile_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Profile,
        obj_in: ProfileUpdate
    ) -> Profile:
        """Update profile."""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_or_update(
        self,
        db: Session,
        *,
        user_id: UUID,
        obj_in: ProfileUpdate
    ) -> Profile:
        """Create profile if it doesn't exist, otherwise update it."""
        existing_profile = self.get_by_user_id(db, user_id=user_id)
        
        if existing_profile:
            return self.update(db, db_obj=existing_profile, obj_in=obj_in)
        else:
            # Create new profile with user_id
            profile_create = ProfileCreate(
                user_id=user_id,
                **obj_in.model_dump(exclude_unset=True)
            )
            return self.create(db, obj_in=profile_create)

    def remove(self, db: Session, *, id: UUID, soft_delete: bool = True) -> Optional[Profile]:
        """Remove profile by UUID (soft delete by default)."""
        obj = db.query(Profile).filter(Profile.id == id).first()
        if obj:
            if soft_delete:
                obj.is_deleted = True
                db.add(obj)
            else:
                db.delete(obj)
            db.commit()
        return obj

    def search_profiles(
        self, 
        db: Session, 
        *, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Profile]:
        """Search profiles by name, bio, location, or company."""
        search_term = f"%{query}%"
        return db.query(Profile).filter(
            Profile.is_profile_public == "public",
            Profile.is_deleted == False,
            (
                Profile.first_name.ilike(search_term) |
                Profile.last_name.ilike(search_term) |
                Profile.bio.ilike(search_term) |
                Profile.location.ilike(search_term) |
                Profile.company.ilike(search_term) |
                Profile.job_title.ilike(search_term)
            )
        ).offset(skip).limit(limit).all()


profile = CRUDProfile()
