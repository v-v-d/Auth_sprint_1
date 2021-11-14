from typing import Any, Union
from app.settings import settings
from app.redis import redis_conn
from abc import ABC, abstractmethod
from enum import Enum
from redis import StrictRedis


class NamespaceEnum(str, Enum):
    black_list = "black_list"
    refresh_list = "refresh_list"


class StorageError(Exception):
    pass


class AbstractStorage(ABC):  # pragma: no cover
    @abstractmethod
    def add(self, key: str) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> None:
        pass

    @abstractmethod
    def check(self, key: str) -> bool:
        pass


class RedisStorage(AbstractStorage):
    def __init__(self, namespace: NamespaceEnum, ttl: int) -> None:
        self.redis: StrictRedis = redis_conn
        self.namespace = namespace
        self.ttl = ttl

    def add(self, key: str, value: Any = "") -> None:
        key = self._build_key(key)
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

    def check(self, key: str) -> bool:
        return self.get(key) is not None

    def _build_key(self, key: str) -> str:
        return f"{self.namespace}:{key}"


black_list_storage = RedisStorage(
    NamespaceEnum.black_list.value, settings.REDIS.BLACK_LIST_TTL
)
refresh_list_storage = RedisStorage(
    NamespaceEnum.refresh_list.value, settings.REDIS.REFRESH_LIST_TTL
)
