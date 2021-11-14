from app.api import BaseJWTResource


@admin_namespace.route("/users/<int:user_id>/has-role/<string:role_name>")
class CheckUserRoleView(BaseJWTResource):
    @admin_namespace.doc("check if user has specific role")
    def get(self, user_id: int, role_name: str):
        user = User.query.get_or_404(user_id)
        return jsonify(has_role=user.has_role(role_name))


@admin_namespace.route("/users/<int:user_id>/set-role/<int:role_id>")
class UserRoleView(BaseJWTResource):
    @admin_namespace.doc("change user role", responses={
        http.HTTPStatus.NOT_FOUND: "Not Found",
    })
    def patch(self, user_id: int, role_id: int):
        user = User.query.get_or_404(user_id)
        role = Role.query.get_or_404(role_id)

        with session_scope():
            user_datastore.add_role_to_user(user, role)
