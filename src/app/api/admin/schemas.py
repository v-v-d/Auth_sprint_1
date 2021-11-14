from flask_restplus import fields

from app.api.admin import namespace

admin_role_schema = namespace.model(
    "Role",
    {
        "id": fields.Integer(),
        "name": fields.String(),
        "description": fields.String(),
        "is_active": fields.Boolean(),
    },
)
