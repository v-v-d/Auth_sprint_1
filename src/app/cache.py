from enum import Enum
from functools import wraps

from flask import Flask
from flask_caching import Cache
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from app.settings import settings


class CacheNamespaceEnum(str, Enum):
    user_roles = "user_roles"
    roles_list = "roles_list"


cache = Cache()


def cached(func):
    """
    Custom decorator for caching the result based on the jwt sub,
    which in the current project is the user ID.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return cache.cached(key_prefix=get_jwt()["sub"])(func)(*args, **kwargs)

    return wrapper


def init_cache(app: Flask):
    app.config["CACHE_TYPE"] = "RedisCache"
    app.config["CACHE_REDIS_URL"] = settings.REDIS.DSN
    app.config["CACHE_DEFAULT_TIMEOUT"] = settings.CACHE_DEFAULT_TIMEOUT

    cache.init_app(app)
