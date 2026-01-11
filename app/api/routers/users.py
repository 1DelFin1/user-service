from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_active_auth_user
from app.exceptions import USER_NOT_FOUND_EXCEPTION
from app.schemas import UserCreateSchema, UserUpdateSchema, UserInDBSchema
from app.services import UserService


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/me")
async def get_current_user(
    user_data: UserInDBSchema = Depends(get_current_active_auth_user),
):
    return user_data


@users_router.post("")
async def create_user(session: SessionDep, user_data: UserCreateSchema):
    user = await UserService.create_user(session, user_data)
    return user


@users_router.get("/{user_id}")
async def get_user_by_id(session: SessionDep, user_id: UUID):
    user = await UserService.get_user_by_id(session, user_id)
    if user is None:
        raise USER_NOT_FOUND_EXCEPTION
    return user


@users_router.get("/{email}")
async def get_user_by_email(session: SessionDep, email: str):
    user = await UserService.get_user_by_email(session, email)
    return user


@users_router.patch("/{user_id}")
async def update_user(session: SessionDep, user_data: UserUpdateSchema, user_id: UUID):
    user = await UserService.update_user(session, user_data, user_id)
    return user


@users_router.delete("/{user_id}")
async def delete_user(session: SessionDep, user_id: UUID):
    user = await UserService.delete_user(session, user_id)
    return user
