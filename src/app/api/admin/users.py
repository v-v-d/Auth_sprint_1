import http

from flask import jsonify

from app.api.admin import namespace
from app.api.base import BaseJWTAdminResource
from app.database import session_scope
from app.datastore import user_datastore
from app.models import User, Role


@namespace.route("/users/<uuid:user_id>/has-role/<string:role_name>")
class CheckUserRoleView(BaseJWTAdminResource):
    @namespace.doc("check if user has specific role")
    def get(self, user_id: int, role_name: str):
        user = User.query.get_or_404(user_id)
        return jsonify(has_role=user.has_role(role_name))


@namespace.route("/users/<uuid:user_id>/set-role/<uuid:role_id>")
class UserRoleView(BaseJWTAdminResource):
    @namespace.doc(
        "change user role",
        responses={
            http.HTTPStatus.NOT_FOUND: "Not Found",
        },
    )
    def patch(self, user_id: int, role_id: int):
        user = User.query.get_or_404(user_id)
        role = Role.query.get_or_404(role_id)

        with session_scope():
            user_datastore.add_role_to_user(user, role)
