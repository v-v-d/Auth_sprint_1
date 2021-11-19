from flask_restplus import fields

from app.api.internal.v1 import namespace

user_info_schema = namespace.model(
    "UserInfo",
    {
        "id": fields.String(),
        "login": fields.String(),
        "email": fields.String(),
        "is_active": fields.Boolean(),
        "roles": fields.List(fields.String(), attribute="roles_names_list"),
    },
)
