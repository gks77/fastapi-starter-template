import uuid
from datetime import date
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema


class ProfileBase(BaseModel):
    """Base profile schema with core profile fields."""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    
    # Social media links
    linkedin_url: Optional[str] = Field(None, max_length=255)
    twitter_url: Optional[str] = Field(None, max_length=255)
    github_url: Optional[str] = Field(None, max_length=255)
    
    # Privacy settings
    is_profile_public: Optional[str] = Field("private", pattern=r"^(public|private|friends)$")
    show_email: Optional[str] = Field("false", pattern=r"^(true|false)$")
    show_phone: Optional[str] = Field("false", pattern=r"^(true|false)$")

    @field_validator('website', 'linkedin_url', 'twitter_url', 'github_url', mode='before')
    @classmethod
    def validate_urls(cls, v: Any) -> Any:
        if v and isinstance(v, str) and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v


class ProfileCreate(ProfileBase, BaseCreateSchema):
    """Schema for creating a profile."""
    user_id: uuid.UUID
    
    # Override base fields to make them optional for creation
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    twitter_url: Optional[str] = Field(None, max_length=255)
    github_url: Optional[str] = Field(None, max_length=255)
    is_profile_public: Optional[str] = Field("private", pattern=r"^(public|private|friends)$")
    show_email: Optional[str] = Field("false", pattern=r"^(true|false)$")
    show_phone: Optional[str] = Field("false", pattern=r"^(true|false)$")


class ProfileUpdate(BaseUpdateSchema):
    """Schema for updating a profile."""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    twitter_url: Optional[str] = Field(None, max_length=255)
    github_url: Optional[str] = Field(None, max_length=255)
    is_profile_public: Optional[str] = Field(None, pattern=r"^(public|private|friends)$")
    show_email: Optional[str] = Field(None, pattern=r"^(true|false)$")
    show_phone: Optional[str] = Field(None, pattern=r"^(true|false)$")


class Profile(ProfileBase, BaseSchema):
    """Schema for profile response with all base fields."""
    user_id: uuid.UUID


class ProfileInDB(Profile):
    """Schema for profile in database."""
    pass


class ProfilePublic(BaseModel):
    """Schema for public profile view (limited fields)."""
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_url: Optional[str] = None
    created_date: Optional[date] = None


class ProfileWithUser(Profile):
    """Schema for profile with basic user information."""
    model_config = ConfigDict(from_attributes=True)
    
    username: Optional[str] = None
    email: Optional[str] = None  # Only shown if show_email is true
