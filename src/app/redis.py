from redis import StrictRedis
from fakeredis import FakeStrictRedis

from app.settings import settings

if settings.TESTING:
    redis_conn = FakeStrictRedis()
else:
    redis_conn = StrictRedis(host=settings.REDIS.HOST, port=settings.REDIS.PORT, decode_responses=True)