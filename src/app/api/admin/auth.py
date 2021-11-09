import http

from flask_jwt_extended import jwt_required
from flask_restplus import Resource
from werkzeug import exceptions

from app.api.admin.namespaces import namespace
from app.api.admin.utils import admin_role_required
from app.api.parsers import role_parser
from app.api.schemas import admin_role_schema
from app.database import session_scope
from app.models import Role


@namespace.route("/roles")
class Role(Resource):
    method_decorators = (jwt_required(), admin_role_required)

    @namespace.doc("get list of roles")
    @namespace.marshal_with(admin_role_schema, as_list=True, code=http.HTTPStatus.OK)
    # @jwt_required()
    # @admin_role_required
    def get(self):
        return Role.query.all()

    @namespace.doc("create role")
    @namespace.expect(role_parser)
    @namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.CREATED)
    # @jwt_required()
    # @admin_role_required
    def post(self):
        with session_scope() as session:
            try:
                new_role = Role(**role_parser.parse_args())
            except Exception:
                raise exceptions.BadRequest("Already exists.")

            session.add(new_role)

        return new_role

    @namespace.doc("change role")
    @namespace.expect(role_parser)
    @namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.OK)
    # @jwt_required()
    # @admin_role_required
    def patch(self, role_id: int):
        with session_scope():
            role = Role.query.get_or_404(id=role_id)

            if role.name in Role.Meta.PROTECTED_ROLE_NAMES:
                raise exceptions.BadRequest("This role is protected.")

            role.update_or_skip(**role_parser.parse_args())

        return role

    @namespace.doc("delete role")
    @namespace.marshal_with("", code=http.HTTPStatus.NO_CONTENT)
    # @jwt_required()
    # @admin_role_required
    def delete(self, role_id: int):
        with session_scope():
            role = Role.query.get_or_404(id=role_id)

            if role.name in Role.Meta.PROTECTED_ROLE_NAMES:
                raise exceptions.BadRequest("This role is protected.")

            role.is_active = False
