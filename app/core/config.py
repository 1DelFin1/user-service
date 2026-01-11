from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    IS_PROD: bool

    DB_USER_SERVICE_HOST: str
    DB_USER_SERVICE_PORT: int
    DB_USER_SERVICE_NAME: str
    DB_USER_SERVICE_USER: str
    DB_USER_SERVICE_PASSWORD: str

    ECHO: bool

    CORS_ORIGINS: list[str]
    CORS_METHODS: list[str]
    CORS_HEADERS: list[str]

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @computed_field
    @property
    def POSTGRES_URL_ASYNC(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.DB_USER_SERVICE_USER,
            password=self.DB_USER_SERVICE_PASSWORD,
            host=self.DB_USER_SERVICE_HOST,
            port=self.DB_USER_SERVICE_PORT,
            path=self.DB_USER_SERVICE_NAME,
        )


settings = Settings()
