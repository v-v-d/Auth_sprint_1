from flask import Flask
from flask_restplus import Api

from app.api import admin, v1

api = Api(
    title="Auth API",
    version="1.0",
    description="Auth API operations",
)

api.add_namespace(admin.namespace)
api.add_namespace(v1.auth.namespace)


def init_api(app: Flask):
    api.init_app(app)
