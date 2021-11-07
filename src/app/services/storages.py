from app.settings import settings
from app.redis import redis_conn


class BlackListStorage:
    def __init__(self, redis_db: redis_conn):
        self.redis_conn = redis_db

    def add(self, token: str):
        redis_conn.set(name=f"black_list: {token}", value="", ex=settings.REDIS.TTL)

    def get_token(self, token: str):
        token_in_black_list = redis_conn.get(name=f"black_list: {token}")
        if token_in_black_list:
            return True


class RefreshListStorage:
    def __init__(self, redis_db: redis_conn):
        self.redis_conn = redis_db

    def add(self, token: str, login_user: str):
        redis_conn.set(name=f"refresh_token: {login_user}", value=token, ex=settings.REDIS.TTL)

    def get_refresh_token(self, login_user: str):
        token_in_black_list = redis_conn.get(name=f"refresh_token: {login_user}", )
        return token_in_black_list is not None


black_list_token = BlackListStorage(redis_db=redis_conn)
refresh_list_token = RefreshListStorage(redis_db=redis_conn)
