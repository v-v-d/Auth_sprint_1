from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import Any, Union, Callable, Optional

from redis.client import Pipeline, StrictRedis

from app.redis import redis_conn
from app.settings import settings


class NamespaceEnum(str, Enum):
    black_list = "black_list"
    refresh_list = "refresh_list"


class StorageError(Exception):
    pass


class AbstractTokenService(ABC):  # pragma: no cover
    @abstractmethod
    def exists_in_black_list(self, refresh_token: str) -> bool:
        pass

    @abstractmethod
    def invalidate_current_refresh_token(self, user_id: int) -> None:
        pass

    @abstractmethod
    def set_new_refresh_token(
        self, old_refresh_token: str, new_refresh_token: str, user_id: int
    ) -> None:
        pass


class TokenService(AbstractTokenService):
    def __init__(self):
        self.redis: StrictRedis = redis_conn

    def exists_in_black_list(self, refresh_token: str) -> bool:
        key = self._build_key(NamespaceEnum.black_list.value, refresh_token)

        try:
            return bool(self.redis.exists(key))
        except Exception as err:
            raise StorageError from err

    def invalidate_current_refresh_token(self, user_id: int) -> None:
        refresh_list_key = self._build_key(NamespaceEnum.refresh_list.value, user_id)
        current_refresh_token = self.redis.get(refresh_list_key)

        if not current_refresh_token:
            # can be removed by TTL
            return

        black_list_key = self._build_key(NamespaceEnum.black_list.value, current_refresh_token)

        try:
            self.redis.set(black_list_key, user_id, ex=settings.BLACK_LIST_TTL)
        except Exception as err:
            raise StorageError from err

    def set_new_refresh_token(
        self, new_refresh_token: str, user_id: int, old_refresh_token: Optional[str]
    ) -> None:
        refresh_list_key = self._build_key(NamespaceEnum.refresh_list.value, user_id)

        if not old_refresh_token:
            old_refresh_token = self.redis.get(refresh_list_key)

        black_list_key = self._build_key(NamespaceEnum.black_list.value, old_refresh_token)

        def callback(pipe: Pipeline) -> None:
            pipe.set(black_list_key, user_id, ex=settings.BLACK_LIST_TTL)
            pipe.set(refresh_list_key, new_refresh_token, ex=settings.REFRESH_LIST_TTL)

        try:
            self.redis.transaction(callback)
        except Exception as err:
            raise StorageError from err

    @staticmethod
    def _build_key(namespace: NamespaceEnum, key: Union[str, int]) -> str:
        return f"{namespace}:{key}"


token_service = TokenService()


class AbstractStorage(ABC):  # pragma: no cover
    @abstractmethod
    def set(self, key: str) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> None:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass


class RedisStorage(AbstractStorage):
    def __init__(self, namespace: NamespaceEnum, ttl: int) -> None:
        self.redis: StrictRedis = redis_conn
        self.pipeline: Pipeline = self.redis.pipeline()
        self.namespace = namespace
        self.ttl = ttl

    @contextmanager
    def transaction(self):
        yield self.pipeline
        self.pipeline.execute()

    def set(self, key: str, value: Any = "", transactional: bool = True) -> None:
        key = self._build_key(key)

        if transactional:
            return self.pipeline.set(name=key, value=value, ex=self.ttl)

        try:
            return self.redis.set(name=key, value=value, ex=self.ttl)
        except Exception as err:
            raise StorageError from err

    def get(self, key: str) -> Union[None, str]:
        key = self._build_key(key)
        try:
            return self.redis.get(name=key)
        except Exception as err:
            raise StorageError from err

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def _build_key(self, key: str) -> str:
        return f"{self.namespace}:{key}"


black_list_storage = RedisStorage(
    NamespaceEnum.black_list.value, settings.BLACK_LIST_TTL
)
refresh_list_storage = RedisStorage(
    NamespaceEnum.refresh_list.value, settings.REFRESH_LIST_TTL
)


def set_new_refresh_token(pipeline):
    pipeline.set()
    pipeline.set()


redis_conn.transaction(set_new_refresh_token)
