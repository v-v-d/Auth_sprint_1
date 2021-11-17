from flask_restplus import fields

from app.api.v1 import namespace

login_schema = namespace.model(
    "Login",
    {
        "access_token": fields.String(),
        "refresh_token": fields.String(),
    },
)

signup_schema = namespace.model(
    "Signup",
    {
        "id": fields.Integer(),
        "login": fields.String(),
        "email": fields.String(),
        "is_active": fields.Boolean(),
    },
)
