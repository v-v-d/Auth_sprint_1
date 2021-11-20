from functools import wraps

from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt
from flask_restplus import Resource
from werkzeug import exceptions

from app.cache import cached
from app.settings import settings


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if get_jwt()["is_admin"]:
            return func(*args, **kwargs)

        raise exceptions.Forbidden()

    return wrapper


class BaseJWTResource(Resource):
    method_decorators = [] if settings.DEBUG else (jwt_required(),)


class BaseJWTCachedResource(Resource):
    method_decorators = [] if settings.DEBUG else (jwt_required(), cached)


class BaseJWTAdminResource(Resource):
    method_decorators = [] if settings.DEBUG else (jwt_required(), admin_required)
