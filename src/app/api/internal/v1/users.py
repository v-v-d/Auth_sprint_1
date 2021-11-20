from flask_jwt_extended import current_user

from app.api.internal.v1 import namespace
from app.api.internal.v1.schemas import user_info_schema
from app.api.base import BaseJWTResource, BaseJWTCachedResource


@namespace.route("/users/info")
class UserInfoView(BaseJWTResource):
    @namespace.doc("get user info")
    @namespace.marshal_with(user_info_schema)
    def get(self):
        return current_user


@namespace.route("/users/roles")
class UserRolesView(BaseJWTCachedResource):
    @namespace.doc("get user roles")
    def get(self):
        return current_user.roles_names_list
