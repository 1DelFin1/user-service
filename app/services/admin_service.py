from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import USER_NOT_FOUND_EXCEPTION, USER_ALREADY_EXIST_EXCEPTION
from app.models.users import UserModel
from app.schemas import UserCreateSchema, UserUpdateSchema
from app.services.base_account_service import BaseAccountService


class AdminService(BaseAccountService):
    model = UserModel
    not_found_exception = USER_NOT_FOUND_EXCEPTION
    already_exists_exception = USER_ALREADY_EXIST_EXCEPTION

    @classmethod
    async def get_admins(cls, session: AsyncSession) -> list[UserModel]:
        stmt = select(cls.model).where(cls.model.is_superuser.is_(True))
        result = await session.scalars(stmt)
        return list(result.all())

    @classmethod
    async def get_admin_by_id(
        cls, session: AsyncSession, admin_id: UUID
    ) -> UserModel | None:
        stmt = select(cls.model).where(
            cls.model.id == admin_id,
            cls.model.is_superuser.is_(True),
        )
        return await session.scalar(stmt)

    @classmethod
    async def get_admin_by_email(
        cls, session: AsyncSession, email: str
    ) -> UserModel | None:
        stmt = select(cls.model).where(
            cls.model.email == email,
            cls.model.is_superuser.is_(True),
        )
        return await session.scalar(stmt)

    @classmethod
    async def create_admin(
        cls, session: AsyncSession, user_data: UserCreateSchema
    ) -> dict[str, bool]:
        admin_data = user_data.model_copy(update={"is_superuser": True})
        return await cls.create(session, admin_data)

    @classmethod
    async def update_admin(
        cls, session: AsyncSession, user_data: UserUpdateSchema, admin_id: UUID
    ) -> dict[str, bool]:
        admin = await cls.get_admin_by_id(session, admin_id)
        if admin is None:
            raise cls.not_found_exception
        return await cls.update(session, user_data, admin_id)

    @classmethod
    async def delete_admin(cls, session: AsyncSession, admin_id: UUID) -> dict[str, bool]:
        admin = await cls.get_admin_by_id(session, admin_id)
        if admin is None:
            raise cls.not_found_exception
        return await cls.delete(session, admin_id)
