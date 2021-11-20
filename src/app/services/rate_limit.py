import datetime
import http

from functools import wraps
from flask_jwt_extended import get_jwt, current_user

from app.redis import redis_conn


def rate_limit(max_calls=20, period=59):

    def func_wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):
            pipe = redis_conn.pipeline()
            now = datetime.datetime.now()
            key = f'{current_user}:{now.minute}'

            pipe.incr(key, 1)
            pipe.expire(key, period)

            result = pipe.execute()
            request_number = result[0]

            if request_number > max_calls:
                return http.HTTPStatus.TOO_MANY_REQUESTS
            else:
                return func(*args, **kwargs)

        return inner

    return func_wrapper
