from datetime import date
from uuid import uuid4, UUID

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base
from app.models.mixins import TimestampMixin


class UserModel(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(50))
    birthday: Mapped[date] = mapped_column(DateTime)
    photo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)
    is_superuser: Mapped[bool] = mapped_column(Boolean)
