import datetime

from datetime import timedelta

from pathlib import Path

from pydantic import BaseSettings, AnyUrl, validator, RedisDsn, PostgresDsn


class WSGISettings(BaseSettings):
    """
    Config for running the app. Not used in main app config.
    """

    app: str = "app.main:app"
    HOST: str = "0.0.0.0"
    PORT: int = 8008
    reload: bool = False
    workers: int = 3

    class Config:
        env_prefix = "WSGI_"


class BaseDSNSettings(BaseSettings):
    USER: str = ""
    PASSWORD: str = ""
    HOST: str = ""
    PORT: int = 0
    PROTOCOL: str = ""
    PATH: str = ""
    DSN: AnyUrl = None

    @validator("DSN", pre=True)
    def build_dsn(cls, v, values) -> str:
        if v:
            return v

        protocol = values["PROTOCOL"]
        user = values["USER"]
        passwd = values["PASSWORD"]
        host = values["HOST"]
        port = values["PORT"]
        path = values["PATH"]

        if user and passwd:
            return f"{protocol}://{user}:{passwd}@{host}:{port}/{path}"

        return f"{protocol}://{host}:{port}/{path}"


class RedisSettings(BaseDSNSettings):
    HOST: str = "api-redis"
    PORT: int = 6379
    BLACK_LIST_TTL: int = 60 * 5
    REFRESH_LIST_TTL: int = 60 * 5
    PROTOCOL: str = "redis"
    DSN: RedisDsn = None

    class Config:
        env_prefix = "REDIS_"


class DatabaseSettings(BaseDSNSettings):
    PROTOCOL: str = "postgresql"
    DSN: PostgresDsn = None
    SCHEMA: str = "content"

    class Config:
        env_prefix = "POSTGRES_"


class JwtSettings(BaseSettings):
    JWT_SECRET_KEY : str = "super-secret"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=30)


class CommonSettings(BaseSettings):
    FLASK_APP: str = "app.main:app"
    ADMIN_LOGIN: str
    ADMIN_PASSWORD: str

    DEBUG: bool = False
    TESTING: bool = False
    LOG_LEVEL: str = "INFO"
    SHARED_DIR: str = "/code/shared"
    DIR_LOGS: Path = Path(SHARED_DIR, "/code/shared/logs")

    WSGI: WSGISettings = WSGISettings()
    REDIS: RedisSettings = RedisSettings()
    DB: DatabaseSettings = DatabaseSettings()

    JWT: JwtSettings = JwtSettings()
