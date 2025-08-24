from fastapi import APIRouter
from app.api.v1.endpoints import auth, user, sessions, profiles, addresses, logs, user_types

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(user_types.router, prefix="/user-types", tags=["user-types"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])
api_router.include_router(logs.router, prefix="/logs", tags=["logging & monitoring"])
