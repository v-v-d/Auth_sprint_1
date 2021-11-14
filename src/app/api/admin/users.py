import http

from flask import jsonify

from app.api.admin import namespace
from app.base import BaseJWTResource
from app.database import session_scope
from app.datastore import user_datastore
from app.models import User, Role


@namespace.route("/users/<int:user_id>/has-role/<string:role_name>")
class CheckUserRoleView(BaseJWTResource):
    @namespace.doc("check if user has specific role")
    def get(self, user_id: int, role_name: str):
        user = User.query.get_or_404(user_id)
        return jsonify(has_role=user.has_role(role_name))


@namespace.route("/users/<int:user_id>/set-role/<int:role_id>")
class UserRoleView(BaseJWTResource):
    @namespace.doc("change user role", responses={
        http.HTTPStatus.NOT_FOUND: "Not Found",
    })
    def patch(self, user_id: int, role_id: int):
        user = User.query.get_or_404(user_id)
        role = Role.query.get_or_404(role_id)

        with session_scope():
            user_datastore.add_role_to_user(user, role)
