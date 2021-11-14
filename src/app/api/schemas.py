from flask_restplus import fields

from app.api import v1

user_schema = {
    "id": fields.Integer(),
    "login": fields.String(),
    "email": fields.String(),
}


auth_schema = {
    'login': fields.String(required=True),
    'password': fields.String(required=True),
}
