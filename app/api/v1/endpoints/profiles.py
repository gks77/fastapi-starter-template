import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.profile import ProfileUpdate, Profile
from app.crud.profile import profile as profile_crud
from app.services.profile_service import profile_service
from app.services.file_upload_service import file_upload_service


router = APIRouter()


@router.get("/me")
def get_my_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Get current user's profile."""
    try:
        profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
        
        if not profile:
            return {
                "message": "Profile not found",
                "has_profile": False,
                "user_id": str(current_user.id)
            }
        
        # Get image URL if avatar exists
        avatar_url = None
        if profile.avatar_url:
            avatar_url = file_upload_service.get_image_url(profile.avatar_url)
        
        # Return basic profile information (working around typing issues)
        return {
            "message": "Profile retrieved successfully",
            "has_profile": True,
            "profile_id": str(profile.id),
            "user_id": str(current_user.id),
            "avatar_url": avatar_url,
            "has_avatar": bool(profile.avatar_url),
            "profile_data": {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "bio": profile.bio,
                "location": profile.location,
                "company": profile.company,
                "job_title": profile.job_title,
                "website": profile.website,
                "linkedin_url": profile.linkedin_url,
                "twitter_url": profile.twitter_url,
                "github_url": profile.github_url,
                "is_profile_public": profile.is_profile_public,
                "show_email": profile.show_email,
                "show_phone": profile.show_phone
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}"
        )


@router.post("/")
def create_or_update_profile(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    profile_data: ProfileUpdate
) -> Dict[str, Any]:
    """Create or update user profile."""
    try:
        # Check if profile already exists
        existing_profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
        
        if existing_profile:
            # Update existing profile
            updated_profile = profile_crud.update(db, db_obj=existing_profile, obj_in=profile_data)
            return {
                "message": "Profile updated successfully",
                "profile_id": str(updated_profile.id),
                "action": "updated"
            }
        else:
            # Create new profile
            from app.schemas.profile import ProfileCreate
            profile_create = ProfileCreate(
                user_id=current_user.id,
                **profile_data.model_dump(exclude_unset=True)
            )
            new_profile = profile_crud.create(db, obj_in=profile_create)
            return {
                "message": "Profile created successfully",
                "profile_id": str(new_profile.id),
                "action": "created"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating profile: {str(e)}"
        )


@router.get("/user/{user_id}")
def get_user_profile(
    user_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Get another user's profile (respects privacy settings)."""
    try:
        profile = profile_crud.get_by_user_id(db, user_id=user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Check privacy settings
        is_own_profile = str(current_user.id) == str(user_id)
        
        # For now, return basic info (due to typing complexities)
        return {
            "message": "Profile found",
            "profile_id": str(profile.id),
            "user_id": str(user_id),
            "is_own_profile": is_own_profile,
            "can_view": is_own_profile or profile.is_profile_public == "public"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}"
        )


@router.get("/search")
def search_profiles(
    q: str = Query(..., min_length=2, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of profiles to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of profiles to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Search public profiles."""
    try:
        profiles = profile_crud.search_profiles(db, query=q, skip=skip, limit=limit)
        
        profile_results = []
        for profile in profiles:
            profile_results.append({
                "profile_id": str(profile.id),
                "user_id": str(profile.user_id),
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "bio": profile.bio,
                "location": profile.location,
                "company": profile.company,
                "job_title": profile.job_title
            })
        
        return {
            "message": f"Found {len(profile_results)} profiles",
            "query": q,
            "results": profile_results,
            "total": len(profile_results),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching profiles: {str(e)}"
        )


@router.delete("/")
def delete_my_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Delete current user's profile (soft delete)."""
    try:
        profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        profile_crud.remove(db, id=profile.id, soft_delete=True)
        
        return {
            "message": "Profile deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile: {str(e)}"
        )


@router.get("/public")
def get_public_profiles(
    skip: int = Query(0, ge=0, description="Number of profiles to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of profiles to return"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Get all public profiles."""
    try:
        profiles = profile_crud.get_public_profiles(db, skip=skip, limit=limit)
        
        profile_results = []
        for profile in profiles:
            profile_results.append({
                "profile_id": str(profile.id),
                "user_id": str(profile.user_id),
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "bio": profile.bio,
                "location": profile.location,
                "company": profile.company,
                "job_title": profile.job_title
            })
        
        return {
            "message": f"Found {len(profile_results)} public profiles",
            "results": profile_results,
            "total": len(profile_results),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving public profiles: {str(e)}"
        )


@router.post("/upload-avatar")
def upload_profile_avatar(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    file: UploadFile = File(..., description="Profile image file (JPG, PNG, GIF, WebP - max 5MB)")
) -> Dict[str, Any]:
    """Upload and update user's profile avatar."""
    try:
        # Save the uploaded image
        image_path = file_upload_service.save_profile_image(file, current_user.id)
        
        # Get or create profile
        existing_profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
        
        if existing_profile:
            # Delete old avatar if exists
            if existing_profile.avatar_url:
                file_upload_service.delete_profile_image(existing_profile.avatar_url)
            
            # Update profile with new avatar
            from app.schemas.profile import ProfileUpdate
            profile_update = ProfileUpdate(avatar_url=image_path)
            updated_profile = profile_crud.update(db, db_obj=existing_profile, obj_in=profile_update)
            
            return {
                "message": "Profile avatar updated successfully",
                "avatar_url": file_upload_service.get_image_url(image_path),
                "file_path": image_path,
                "profile_id": str(updated_profile.id)
            }
        else:
            # Create new profile with avatar
            from app.schemas.profile import ProfileCreate
            profile_create = ProfileCreate(
                user_id=current_user.id,
                avatar_url=image_path
            )
            new_profile = profile_crud.create(db, obj_in=profile_create)
            
            return {
                "message": "Profile created with avatar successfully",
                "avatar_url": file_upload_service.get_image_url(image_path),
                "file_path": image_path,
                "profile_id": str(new_profile.id)
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading avatar: {str(e)}"
        )


@router.delete("/avatar")
def delete_profile_avatar(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Delete user's profile avatar."""
    try:
        profile = profile_crud.get_by_user_id(db, user_id=current_user.id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        if not profile.avatar_url:
            return {
                "message": "No avatar to delete",
                "had_avatar": False
            }
        
        # Delete the image file
        file_deleted = file_upload_service.delete_profile_image(profile.avatar_url)
        
        # Update profile to remove avatar URL
        from app.schemas.profile import ProfileUpdate
        profile_update = ProfileUpdate(avatar_url=None)
        profile_crud.update(db, db_obj=profile, obj_in=profile_update)
        
        return {
            "message": "Profile avatar deleted successfully",
            "file_deleted": file_deleted,
            "had_avatar": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting avatar: {str(e)}"
        )
