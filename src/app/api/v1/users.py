from flask_jwt_extended import get_jwt, current_user
from werkzeug import exceptions

from app.api.base import BaseJWTResource
from app.api.v1 import namespace
from app.api.v1.parsers import user_password_parser, user_history_parser
from app.api.v1.schemas import user_history_schema
from app.database import session_scope
from app.models import AuthHistory
from app.services.accounts import AccountsService, AccountsServiceError


@namespace.route("/users/update-password")
class UsersView(BaseJWTResource):
    @namespace.doc("update user password")
    @namespace.expect(user_password_parser)
    def patch(self):
        args = user_password_parser.parse_args()

        if not current_user.check_password(args["old_password"]):
            raise exceptions.BadRequest()

        jti = get_jwt()["jti"]

        try:
            with session_scope():
                current_user.password = args["new_password"]
                AccountsService.logout(jti, current_user.id)
        except AccountsServiceError:
            raise exceptions.FailedDependency()


@namespace.route("/users/history")
class UserHistoryView(BaseJWTResource):
    @namespace.doc("get list of user history")
    @namespace.expect(user_history_parser)
    @namespace.marshal_with(user_history_schema, as_list=True)
    def get(self):
        args = user_history_parser.parse_args()
        queryset = AuthHistory.query.filter_by(user_id=current_user.id).order_by(
            AuthHistory.timestamp.asc()
        )
        paginator = queryset.paginate(
            page=args["page"], per_page=args["per_page"], error_out=False
        )

        return paginator.items
