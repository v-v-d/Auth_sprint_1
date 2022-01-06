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
    PROTOCOL: str = "redis"
    DSN: RedisDsn = None

    class Config:
        env_prefix = "REDIS_"


class RateLimitSettings(BaseSettings):
    MAX_CALLS: int = 20
    PERIOD: int = 59

    class Config:
        env_prefix = "RATE_LIMIT_"


class DatabaseSettings(BaseDSNSettings):
    PROTOCOL: str = "postgresql"
    DSN: PostgresDsn = None
    SCHEMA: str = "content"

    class Config:
        env_prefix = "POSTGRES_"


class JWTSettings(BaseSettings):
    SECRET_KEY: str = "super-secret"
    ACCESS_TOKEN_EXPIRES: int = 60
    REFRESH_TOKEN_EXPIRES: int = 60 * 60 * 24 * 30  # 30 days

    class Config:
        env_prefix = "JWT_"


class JaegerSettings(BaseSettings):
    ENABLED: bool = True
    TYPE: str = "const"
    REPORTING_HOST: str = "jaeger"
    REPORTING_PORT: int = 6831
    SERVICE_NAME: str = "auth_app"
    TRACE_ID_HEADER: str = "X-Request-Id"

    class Config:
        env_prefix = "JAEGER_"


class OauthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_SERVER_METADATA_URL: str = ""

    YANDEX_CLIENT_ID: str = ""
    YANDEX_CLIENT_SECRET: str = ""
    YANDEX_API_BASE_URL: str = ""
    YANDEX_ACCESS_TOKEN_URL: str = ""
    YANDEX_AUTHORIZE_URL: str = ""
    YANDEX_USERINFO_ENDPOINT: str = ""

    class Config:
        env_prefix = "OAUTH_"


class SecuritySettings(BaseSettings):
    SECRET_KEY: str = ""
    DEFAULT_ADMIN_LOGIN: str
    DEFAULT_ADMIN_PASSWORD: str

    class Config:
        env_prefix = "SECURITY_"


class CommonSettings(BaseSettings):
    FLASK_APP: str = "app.main:app"

    DEBUG: bool = False
    TESTING: bool = False
    LOG_LEVEL: str = "INFO"
    SHARED_DIR: str = "/code/shared"
    DIR_LOGS: Path = Path(SHARED_DIR, "/code/shared/logs")

    WSGI: WSGISettings = WSGISettings()
    REDIS: RedisSettings = RedisSettings()
    DB: DatabaseSettings = DatabaseSettings()
    JWT: JWTSettings = JWTSettings()
    RATE_LIMIT: RateLimitSettings = RateLimitSettings()
    OAUTH: OauthSettings = OauthSettings()
    SECURITY: SecuritySettings = SecuritySettings()
    JAEGER: JaegerSettings = JaegerSettings()

    DEFAULT_PAGE_LIMIT: int = 5
    CACHE_DEFAULT_TIMEOUT: int = 60 * 60 * 3
