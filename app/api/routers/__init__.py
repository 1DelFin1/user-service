__all__ = ("main_router",)

from fastapi import APIRouter

from app.api.routers.users import users_router
from app.api.routers.auth import auth_router
from app.api.routers.sellers import sellers_router
from app.api.routers.admins import admins_router


main_router = APIRouter()
main_router.include_router(users_router)
main_router.include_router(auth_router)
main_router.include_router(sellers_router)
main_router.include_router(admins_router)
