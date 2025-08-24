from sqlalchemy import Column, String, Text, Date, Integer
from sqlalchemy.orm import relationship
from app.db.base import BaseModel, GUID


class Profile(BaseModel):
    """Profile model for storing user profile information."""
    
    __tablename__ = "profiles"

    user_id = Column(GUID(), nullable=False, unique=True, index=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)  # Additional image attribute
    location = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    company = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    
    # Social media links
    linkedin_url = Column(String(255), nullable=True)
    twitter_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    
    # Privacy settings
    is_profile_public = Column(String(10), default="private", nullable=False)  # public, private, friends
    show_email = Column(String(10), default="false", nullable=False)  # true, false
    show_phone = Column(String(10), default="false", nullable=False)  # true, false
    
    # The following fields are inherited from BaseModel:
    # - id (UUID, primary key)
    # - created_date (DateTime) - when profile was created
    # - updated_date (DateTime) - when profile was last updated
    # - other_details (JSON) - for additional profile metadata
    # - is_deleted (Boolean) - for soft delete of profiles
