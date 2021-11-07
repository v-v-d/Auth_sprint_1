from app.settings import settings
from app.redis import redis_conn


class Namespace:
    black = "black_list"
    refresh = "refresh_token"


class BlackListStorage:
    def __init__(self, redis_db: redis_conn):
        self.redis_conn = redis_db

    def add(self, token: str):
        redis_conn.set(name=f"{Namespace.black}: {token}", value="", ex=settings.REDIS.TTL)

    def check(self, token: str):
        token_in_black_list = redis_conn.get(name=f"{Namespace.black}: {token}")
        return token_in_black_list is not None


class RefreshListStorage:
    def __init__(self, redis_db: redis_conn):
        self.redis_conn = redis_db

    def add(self, token: str, login_user: str):
        redis_conn.set(name=f"{Namespace.refresh}: {login_user}", value=token, ex=settings.REDIS.TTL)

    def get_refresh_token(self, login_user: str):
        token_in_black_list = redis_conn.get(name=f"{Namespace.refresh}: {login_user}")
        return token_in_black_list


black_list_token = BlackListStorage(redis_db=redis_conn)
refresh_list_token = RefreshListStorage(redis_db=redis_conn)
