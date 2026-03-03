from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import USER_NOT_FOUND_EXCEPTION, USER_ALREADY_EXIST_EXCEPTION
from app.models.users import UserModel
from app.schemas import UserCreateSchema, UserUpdateSchema
from app.services.base_account_service import BaseAccountService


class UserService(BaseAccountService):
    model = UserModel
    not_found_exception = USER_NOT_FOUND_EXCEPTION
    already_exists_exception = USER_ALREADY_EXIST_EXCEPTION

    @classmethod
    async def get_user_by_id(
        cls, session: AsyncSession, user_id: UUID
    ) -> UserModel | None:
        return await cls.get_by_id(session, user_id)

    @classmethod
    async def get_user_by_email(
        cls, session: AsyncSession, email: str
    ) -> UserModel | None:
        return await cls.get_by_email(session, email)

    @classmethod
    async def create_user(cls, session: AsyncSession, user_data: UserCreateSchema):
        return await cls.create(session, user_data)

    @classmethod
    async def update_user(
        cls, session: AsyncSession, user_data: UserUpdateSchema, user_id: UUID
    ):
        return await cls.update(session, user_data, user_id)

    @classmethod
    async def delete_user(cls, session: AsyncSession, user_id: UUID):
        return await cls.delete(session, user_id)
