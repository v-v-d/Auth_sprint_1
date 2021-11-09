from functools import wraps

from flask_jwt_extended import get_jwt_identity
from werkzeug import exceptions


def admin_role_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_jwt_identity()

        if not user.is_staff:
            raise exceptions.Forbidden()

        return func(*args, **kwargs)

    return wrapper
