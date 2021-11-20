import http

from flask_jwt_extended import get_jwt, current_user
from werkzeug import exceptions
from flask import jsonify

from app.api.v1 import namespace
from app.api.v1.parsers import user_password_parser, user_history_parser
from app.api.v1.schemas import user_history_schema
from app.base import BaseJWTResource
from app.database import session_scope
from app.models import User, AuthHistory
from app.services.accounts import AccountsService
from app.services.storages import TokenStorageError


@namespace.route("/users/<uuid:user_id>/update-password")
class UsersView(BaseJWTResource):
    @namespace.doc("update user password")
    @namespace.expect(user_password_parser)
    def patch(self, user_id: int):
        if current_user == user_id:
            user = User.query.get_or_404(user_id)
            args = user_password_parser.parse_args()

            if not user.check_password(args["old_password"]):
                raise exceptions.BadRequest()

            try:
                with session_scope():
                    user.password = args["new_password"]
                    AccountsService.logout(get_jwt()["jti"], user.id)
            except TokenStorageError:
                raise exceptions.FailedDependency()
            return jsonify(message='Ok')
        return "You don't have enough rights"


@namespace.route("/users/<uuid:user_id>/history")
class UserHistoryView(BaseJWTResource):
    @namespace.doc("get list of user history")
    @namespace.expect(user_history_parser)
    @namespace.marshal_with(user_history_schema, as_list=True, code=http.HTTPStatus.OK)
    def get(self, user_id):
        if current_user == user_id:  # or User.query.get(current_user).role is 'superuser':
            args = user_history_parser.parse_args()
            queryset = AuthHistory.query.filter_by(user_id=user_id).order_by(
                AuthHistory.timestamp.asc()
            )
            paginator = queryset.paginate(
                page=args["page"], per_page=args["per_page"], error_out=False
            )

            return paginator.items

        return jsonify(message="You don't have enough rights")
