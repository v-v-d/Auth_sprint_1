from redis import StrictRedis

from app.settings import settings

redis_conn = StrictRedis(
    host=settings.REDIS.HOST, port=settings.REDIS.PORT, decode_responses=True
)
