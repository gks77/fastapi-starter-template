# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.user_type import UserType
from app.models.address import Address
from app.models.profile import Profile
from app.models.session import Session

__all__ = ["User", "UserType", "Address", "Profile", "Session"]
