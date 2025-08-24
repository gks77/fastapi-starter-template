import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session as DBSession
from fastapi import HTTPException, status

from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfilePublic, ProfileWithUser
from app.crud.profile import profile as profile_crud
from app.crud.user import user as user_crud


class ProfileService:
    """Service for managing user profiles."""
    
    def get_profile(self, db: DBSession, *, user_id: uuid.UUID) -> Optional[Profile]:
        """Get profile by user ID."""
        return profile_crud.get_by_user_id(db, user_id=user_id)
    
    def get_my_profile(self, db: DBSession, *, current_user: User) -> Optional[Profile]:
        """Get current user's profile."""
        return profile_crud.get_by_user_id(db, user_id=current_user.id)
    
    def create_or_update_profile(
        self, 
        db: DBSession, 
        *, 
        current_user: User,
        profile_data: ProfileUpdate
    ) -> Profile:
        """Create or update user profile."""
        return profile_crud.create_or_update(
            db, 
            user_id=current_user.id, 
            obj_in=profile_data
        )
    
    def get_public_profile(
        self, 
        db: DBSession, 
        *, 
        user_id: uuid.UUID,
        requesting_user_id: Optional[uuid.UUID] = None
    ) -> Optional[ProfilePublic]:
        """Get public profile view."""
        profile = profile_crud.get_by_user_id(db, user_id=user_id)
        
        if not profile:
            return None
        
        # Check if profile is public or if it's the owner viewing
        if profile.is_profile_public == "private" and requesting_user_id != user_id:
            return None
        
        # Convert to public profile schema
        return ProfilePublic(
            id=profile.id,
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            location=profile.location,
            website=profile.website,
            company=profile.company,
            job_title=profile.job_title,
            linkedin_url=profile.linkedin_url,
            twitter_url=profile.twitter_url,
            github_url=profile.github_url,
            created_date=profile.created_date.date() if profile.created_date else None
        )
    
    def get_profile_with_user_info(
        self, 
        db: DBSession, 
        *, 
        user_id: uuid.UUID,
        requesting_user_id: Optional[uuid.UUID] = None
    ) -> Optional[ProfileWithUser]:
        """Get profile with user information."""
        profile = profile_crud.get_by_user_id(db, user_id=user_id)
        user = user_crud.get(db, id=user_id)
        
        if not profile or not user:
            return None
        
        # Check privacy settings
        if profile.is_profile_public == "private" and requesting_user_id != user_id:
            return None
        
        # Determine what information to show based on privacy settings
        email_to_show = None
        if profile.show_email == "true" or requesting_user_id == user_id:
            email_to_show = user.email
        
        # Create the response
        profile_data = ProfileWithUser(
            **profile.__dict__,
            username=user.username,
            email=email_to_show
        )
        
        return profile_data
    
    def search_public_profiles(
        self, 
        db: DBSession, 
        *, 
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProfilePublic]:
        """Search public profiles."""
        profiles = profile_crud.search_profiles(
            db, 
            query=query, 
            skip=skip, 
            limit=limit
        )
        
        public_profiles = []
        for profile in profiles:
            public_profile = ProfilePublic(
                id=profile.id,
                user_id=profile.user_id,
                first_name=profile.first_name,
                last_name=profile.last_name,
                bio=profile.bio,
                avatar_url=profile.avatar_url,
                location=profile.location,
                website=profile.website,
                company=profile.company,
                job_title=profile.job_title,
                linkedin_url=profile.linkedin_url,
                twitter_url=profile.twitter_url,
                github_url=profile.github_url,
                created_date=profile.created_date.date() if profile.created_date else None
            )
            public_profiles.append(public_profile)
        
        return public_profiles
    
    def delete_profile(
        self, 
        db: DBSession, 
        *, 
        current_user: User
    ) -> bool:
        """Delete user's profile (soft delete)."""
        profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
        if profile:
            profile_crud.remove(db, id=profile.id, soft_delete=True)
            return True
        return False


profile_service = ProfileService()
