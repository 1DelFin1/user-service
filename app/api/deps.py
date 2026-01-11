from typing import Annotated
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import JWTAuthenticator
from app.core.database import async_session_factory
from app.exceptions import (
    USER_NOT_FOUND_EXCEPTION,
    USER_UNAUTHORIZED_EXCEPTION,
    INVALID_TOKEN_EXCEPTION,
)
from app.services import UserService


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_active_auth_user(request: Request, session: SessionDep):
    token = request.cookies.get("token")
    if not token:
        raise USER_UNAUTHORIZED_EXCEPTION

    try:
        payload = JWTAuthenticator.decode_jwt_token(token)
    except InvalidTokenError:
        raise INVALID_TOKEN_EXCEPTION

    user = await UserService.get_user_by_email(session, payload.get("email"))
    if not user:
        raise USER_NOT_FOUND_EXCEPTION

    return user
