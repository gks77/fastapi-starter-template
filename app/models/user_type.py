"""
User Type model for categorizing different types of users in the system.
"""

from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import BaseModel


class UserType(BaseModel):
    """
    User Type model to categorize users (ADMIN, USER, EMPLOYEE, HR, SUPER_ADMIN).
    This is a lookup table that gets initialized when the application starts.
    """
    __tablename__ = "user_types"

    name = Column(String(50), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship with users
    users = relationship("User", back_populates="user_type")

    def __repr__(self):
        return f"<UserType(id={self.id}, name='{self.name}', code='{self.code}')>"

    def __str__(self):
        return self.name
