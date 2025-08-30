from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
    email: EmailStr = Field(max_length=255)
    name: str = Field(max_length=50)
    birthday: date | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreateSchema(UserBaseSchema):
    password: str = Field(max_length=40)


class UserUpdateSchema(BaseModel):
    email: str | None = None
    name: str | None = None
    birthday: date | None = None
    password: str | None = None


class UserOutSchema(UserBaseSchema):
    id: UUID

    class Config:
        from_attributes = True


class UserInDBSchema(UserBaseSchema):
    id: UUID
    hashed_password: str
