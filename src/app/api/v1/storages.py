from app.settings import settings
from app.main import redis_conn


class BlackListStorage:
    def __init__(self, redis_db: redis_conn, token: str):
        self.redis_conn = redis_db
        self.token = token

    def adding_token_black_list(self):
        redis_conn.set(name="jwt_black_list", value=self.token, ex=settings.REDIS.TTL)

    def get_token_black_list(self):
        token_in_black_list = redis_conn.getset(name="jwt_black_list", value=self.token)
        return token_in_black_list is not None


class RefreshListStorage:
    def __init__(self, redis_db: redis_conn, token: str):
        self.redis_conn = redis_db
        self.token = token

    def adding_refresh_token(self):
        redis_conn.set(name="jwt_refresh_token", value=self.token, ex=settings.REDIS.TTL)

    def get_refresh_token(self):
        token_in_black_list = redis_conn.getset(name="jwt_refresh_token", value=self.token)
        return token_in_black_list is not None
