from flask_jwt_extended import jwt_required
from flask_restplus import Resource

from app.settings import settings


class BaseJWTResource(Resource):
    method_decorators = [] if settings.DEBUG else (jwt_required(), )
