from functools import wraps

from flask_jwt_extended import verify_jwt_in_request, get_jwt
from werkzeug import exceptions


def admin_required():
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if claims["is_admin"]:
                return func(*args, **kwargs)

            raise exceptions.Forbidden()

        return decorator
    return wrapper
