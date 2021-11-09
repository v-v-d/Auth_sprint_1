from flask_restplus import fields

from app.api import admin, v1

user_schema = {
    "id": fields.Integer(),
    "username": fields.String(),
    "email": fields.String(),
}

role_schema = {
    "id": fields.Integer(),
    "name": fields.String(),
    "description": fields.String(),
    "is_active": fields.Boolean(),
}

auth_user_schema = v1.auth.namespace.model("User", user_schema)
admin_role_schema = admin.namespace.model("Role", role_schema)
