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

user_history_schema = namespace.model(
    "User_history",
    {
        "id": fields.Integer(),
        "timestamp": fields.DateTime(),
        "user_agent": fields.String(),
        "ip_addr": fields.String(),
        "device": fields.String(),
    },
)
