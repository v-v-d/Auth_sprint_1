from flask import Flask
from flask_restplus import Api

from app.api.admin import namespace as admin_namespace
from app.api.v1 import namespace as api_v1_namespace
from app.api.internal.v1 import namespace as internal_api_v1_namespace

api = Api(
    title="Auth API",
    version="1.0",
    description="Auth API operations",
)

api.add_namespace(admin_namespace)
api.add_namespace(api_v1_namespace)
api.add_namespace(internal_api_v1_namespace)


def init_api(app: Flask):
    api.init_app(app)
