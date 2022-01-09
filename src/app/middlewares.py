from datetime import datetime

from flask import Flask, request
from redis.client import Pipeline
from werkzeug import exceptions

from app.redis import redis_conn
from app.settings import settings


def rate_limit_middleware():
    dt = datetime.now().replace(second=0, microsecond=0)
    key = f"{request.remote_addr}:{dt}"
    increment_step = 1

    def callback(pipe: Pipeline) -> None:
        pipe.incr(key, increment_step)
        pipe.expire(key, settings.RATE_LIMIT.PERIOD)

    request_number, _ = redis_conn.transaction(func=callback)

    if request_number > settings.RATE_LIMIT.MAX_CALLS:
        raise exceptions.TooManyRequests()


def tracing_middleware():
    if not settings.TRACING.ENABLED:
        return

    if not request.headers.get(settings.TRACING.TRACE_ID_HEADER):
        raise exceptions.BadRequest(f"{settings.TRACING.TRACE_ID_HEADER} is required.")


def init_middlewares(app: Flask):
    @app.before_request
    def apply_middlewares():
        rate_limit_middleware()
        tracing_middleware()
