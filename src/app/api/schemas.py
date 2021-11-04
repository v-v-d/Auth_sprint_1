from flask_restplus import fields

from app.api import v1

user_schema = {
    "id": fields.Integer(),
    "username": fields.String(),
    "email": fields.String(),
}

auth_user_schema = v1.auth.namespace.model("User", user_schema)
