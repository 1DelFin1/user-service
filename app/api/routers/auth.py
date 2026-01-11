from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.api.deps import SessionDep
from app.api.utils import Authorization
from app.api.request_forms import OAuth2EmailRequestForm


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@auth_router.post("/login")
async def login(
    session: SessionDep,
    form_data: Annotated[OAuth2EmailRequestForm, Depends()],
    response: Response,
):
    await Authorization.login(session, form_data, response)
    return {"message": "Logged is successfully", "ok": True}


@auth_router.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"message": "Successfully logged out", "ok": True}
