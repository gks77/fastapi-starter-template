"""
Extended user schemas that include relationships.
This file handles schemas that require imports from other schema modules.
"""

from typing import Optional, TYPE_CHECKING
from app.schemas.user import User as BaseUser

if TYPE_CHECKING:
    from app.schemas.user_type import UserType


class UserWithType(BaseUser):
    """User schema that includes the user_type relationship."""
    user_type: Optional["UserType"] = None

    class Config:
        from_attributes = True
