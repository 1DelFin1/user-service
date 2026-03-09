from urllib.parse import urlparse
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import USER_NOT_FOUND_EXCEPTION, USER_ALREADY_EXIST_EXCEPTION
from app.models.users import UserModel
from app.schemas import UserCreateSchema, UserUpdateSchema
from app.services.base_account_service import BaseAccountService
from app.services.minio_service import MinioService


class UserService(BaseAccountService):
    model = UserModel
    not_found_exception = USER_NOT_FOUND_EXCEPTION
    already_exists_exception = USER_ALREADY_EXIST_EXCEPTION

    @staticmethod
    def _resolve_image_extension(filename: str, content_type: str) -> str:
        if "." in filename:
            extension = filename.rsplit(".", 1)[-1].lower().strip()
            if extension:
                return extension

        content_type_to_extension = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
            "image/bmp": "bmp",
        }
        return content_type_to_extension.get(content_type, "bin")

    @staticmethod
    def _extract_object_key_from_public_url(
        photo_url: str,
        *,
        bucket_name: str,
    ) -> str | None:
        parsed = urlparse(photo_url)
        path = parsed.path.lstrip("/")
        bucket_prefix = f"{bucket_name}/"
        if not path.startswith(bucket_prefix):
            return None
        object_key = path[len(bucket_prefix):]
        return object_key or None

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

    @classmethod
    async def upload_user_photo(
        cls,
        session: AsyncSession,
        user_id: UUID,
        file: UploadFile,
    ) -> UserModel:
        user = await cls.get_user_by_id(session, user_id)
        if user is None:
            raise USER_NOT_FOUND_EXCEPTION

        content_type = file.content_type or "application/octet-stream"
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed",
            )

        file_data = await file.read()
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image is empty",
            )

        minio_service = MinioService()
        file_extension = cls._resolve_image_extension(file.filename or "", content_type)
        object_key = f"users/{user_id}/avatar_{uuid4()}.{file_extension}"
        photo_url = minio_service.upload_file(
            file_data=file_data,
            filename=object_key,
            content_type=content_type,
        )

        previous_photo_url = user.photo_url.strip() if isinstance(user.photo_url, str) else None
        user.photo_url = photo_url
        session.add(user)
        await session.commit()
        await session.refresh(user)

        if previous_photo_url:
            previous_object_key = cls._extract_object_key_from_public_url(
                previous_photo_url,
                bucket_name=minio_service.bucket_name,
            )
            if previous_object_key and previous_object_key != object_key:
                try:
                    minio_service.delete_file(previous_object_key)
                except HTTPException:
                    pass

        return user
