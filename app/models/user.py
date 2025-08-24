from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.db.base import GUID


class User(BaseModel):
    """User model extending from BaseModel."""
    
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # User type reference
    user_type_id = Column(GUID, ForeignKey("user_types.id"), nullable=True, index=True)
    
    # Image attribute
    image_url = Column(String(500), nullable=True)
    
    # Relationships
    user_type = relationship("UserType", back_populates="users")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def default_address(self):
        """Get the default address for this user."""
        for address in self.addresses:
            if address.is_default and address.is_active:
                return address
        return None
