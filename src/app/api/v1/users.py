from flask_jwt_extended import get_jwt
from werkzeug import exceptions

from app.api.v1 import namespace
from app.api.v1.parsers import user_password_parser
from app.base import BaseJWTResource
from app.database import session_scope
from app.models import User
from app.services.accounts import AccountsService
from app.services.storages import TokenStorageError


@namespace.route("/users/<uuid:user_id>/update-password")
class UsersView(BaseJWTResource):
    @namespace.doc("update user password")
    @namespace.expect(user_password_parser)
    def patch(self, user_id: int):
        args = user_password_parser.parse_args()

        user = User.query.get_or_404(user_id)

        if not user.check_password(args["old_password"]):
            raise exceptions.BadRequest()

        try:
            with session_scope():
                user.password = args["new_password"]
                AccountsService.logout(get_jwt()["jti"], user.id)
        except TokenStorageError:
            raise exceptions.FailedDependency()
