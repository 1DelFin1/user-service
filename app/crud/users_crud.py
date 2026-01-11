from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import USER_NOT_FOUND_EXCEPTION
from app.schemas import UserCreateSchema, UserUpdateSchema
from app.core.security import get_password_hash
from app.models.users import UserModel


async def create_user(session: AsyncSession, user_data: UserCreateSchema):
    user = user_data.model_dump(exclude={"password"})
    user["hashed_password"] = get_password_hash(user_data.password)
    new_user = UserModel(**user)
    session.add(new_user)

    await session.commit()
    return {"ok": True}


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> UserModel:
    stmt = select(UserModel).where(UserModel.id == user_id)
    user = await session.scalar(stmt)
    if not user:
        raise USER_NOT_FOUND_EXCEPTION
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> UserModel:
    stmt = select(UserModel).where(UserModel.email == email)
    user = await session.scalar(stmt)
    if not user:
        raise USER_NOT_FOUND_EXCEPTION
    return user


async def update_user(
    session: AsyncSession, user_data: UserUpdateSchema, user_id: UUID
):
    user = await get_user_by_id(session, user_id)

    new_user = user_data.model_dump(exclude_unset=True)
    if "password" in new_user:
        new_user["hashed_password"] = get_password_hash(user_data.password)
        del new_user["password"]
    for key, value in new_user.items():
        if new_user[key] != "":
            setattr(user, key, value)
    await session.refresh(user)
    return {"ok": True}


async def delete_user(session: AsyncSession, user_id: UUID):
    user = await get_user_by_id(session, user_id)
    await session.delete(user)
    await session.commit()
    return {"ok": True}
