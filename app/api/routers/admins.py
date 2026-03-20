from uuid import UUID

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.exceptions import USER_NOT_FOUND_EXCEPTION
from app.schemas import UserCreateSchema, UserUpdateSchema, UserOutSchema
from app.services import AdminService


admins_router = APIRouter(prefix="/admins", tags=["admins"])


@admins_router.get("", response_model=list[UserOutSchema])
async def get_admins(session: SessionDep):
    return await AdminService.get_admins(session)


@admins_router.post("")
async def create_admin(session: SessionDep, user_data: UserCreateSchema):
    return await AdminService.create_admin(session, user_data)


@admins_router.get("/{admin_id}", response_model=UserOutSchema)
async def get_admin_by_id(session: SessionDep, admin_id: UUID):
    admin = await AdminService.get_admin_by_id(session, admin_id)
    if admin is None:
        raise USER_NOT_FOUND_EXCEPTION
    return admin


@admins_router.get("/by-email/{email}", response_model=UserOutSchema)
async def get_admin_by_email(session: SessionDep, email: str):
    admin = await AdminService.get_admin_by_email(session, email)
    if admin is None:
        raise USER_NOT_FOUND_EXCEPTION
    return admin


@admins_router.patch("/{admin_id}")
async def update_admin(
    session: SessionDep, user_data: UserUpdateSchema, admin_id: UUID
):
    return await AdminService.update_admin(session, user_data, admin_id)


@admins_router.delete("/{admin_id}")
async def delete_admin(session: SessionDep, admin_id: UUID):
    return await AdminService.delete_admin(session, admin_id)
