from abc import ABC, abstractmethod
from uuid import UUID

from redis.client import StrictRedis, Pipeline

from app.redis import redis_conn
from app.settings import settings
from app.tracing import traced


class BaseTokenStorageError(Exception):
    pass


class TokenStorageError(BaseTokenStorageError):
    pass


class InvalidTokenError(BaseTokenStorageError):
    pass


class AbstractTokenStorage(ABC):  # pragma: no cover
    @abstractmethod
    def validate_refresh_token(self, refresh_token: str, user_id: int) -> bool:
        pass

    @abstractmethod
    def invalidate_current_refresh_token(self, user_id: int) -> None:
        pass

    @abstractmethod
    def set_refresh_token(self, new_refresh_token: str, user_id: int) -> None:
        pass


class RedisTokenStorage(AbstractTokenStorage):
    def __init__(self):
        self.redis: StrictRedis = redis_conn

    def validate_refresh_token(self, refresh_token_jti: str, user_id: UUID) -> None:
        current_refresh_token_jti = self._execute(self.redis.get, name=str(user_id))

        if not current_refresh_token_jti:
            # Reuse was previously detected and token was invalidated
            raise InvalidTokenError

        if current_refresh_token_jti != refresh_token_jti:
            raise InvalidTokenError

        return

    def validate_access_token(self, access_token_jti: str) -> bool:
        return bool(self._execute(self.redis.exists, access_token_jti))

    def invalidate_current_refresh_token(self, user_id: UUID) -> None:
        self._execute(self.redis.delete, str(user_id))

    def set_refresh_token(self, token_jti: str, user_id: UUID) -> None:
        self._execute(self.redis.set, name=str(user_id), value=token_jti)

    def invalidate_token_pair(self, access_token_jti: str, user_id: UUID) -> None:
        def callback(pipe: Pipeline) -> None:
            pipe.set(
                name=access_token_jti,
                value=str(user_id),
                ex=settings.JWT.ACCESS_TOKEN_EXPIRES,
            )
            pipe.delete(str(user_id))

        self._execute(self.redis.transaction, func=callback)

    @staticmethod
    @traced("Redis token storage")
    def _execute(method, *args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as err:
            raise TokenStorageError from err


token_storage = RedisTokenStorage()
