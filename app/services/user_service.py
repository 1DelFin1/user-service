from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.exceptions import USER_NOT_FOUND_EXCEPTION, USER_ALREADY_EXIST_EXCEPTION
from app.models.users import UserModel
from app.schemas import UserCreateSchema, UserUpdateSchema


class UserService:
    @classmethod
    async def get_user_by_id(
        cls, session: AsyncSession, user_id: UUID
    ) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user = await session.scalar(stmt)
        if not user:
            return None
        return user

    @classmethod
    async def get_user_by_email(
        cls, session: AsyncSession, email: str
    ) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        user = await session.scalar(stmt)
        if not user:
            return None
        return user

    @classmethod
    async def create_user(cls, session: AsyncSession, user_data: UserCreateSchema):
        if await cls.get_user_by_email(session, user_data.email):
            raise USER_ALREADY_EXIST_EXCEPTION

        user = user_data.model_dump(exclude={"password"})
        user["hashed_password"] = get_password_hash(user_data.password)
        new_user = UserModel(**user)
        session.add(new_user)

        await session.commit()
        return {"ok": True}

    @classmethod
    async def update_user(
        cls, session: AsyncSession, user_data: UserUpdateSchema, user_id: UUID
    ):
        user = await cls.get_user_by_id(session, user_id)
        if user is None:
            raise USER_NOT_FOUND_EXCEPTION

        new_user = user_data.model_dump(exclude_unset=True)
        if "password" in new_user:
            new_user["hashed_password"] = get_password_hash(user_data.password)
            del new_user["password"]
        for key, value in new_user.items():
            if new_user[key] != "":
                setattr(user, key, value)

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return {"ok": True}

    @classmethod
    async def delete_user(cls, session: AsyncSession, user_id: UUID):
        user = await cls.get_user_by_id(session, user_id)
        if user is None:
            raise USER_NOT_FOUND_EXCEPTION

        await session.delete(user)
        await session.commit()
        return {"ok": True}
