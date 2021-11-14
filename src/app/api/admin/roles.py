import http

from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions

from app.api.admin import namespace
from app.api.admin.parsers import role_list_parser, role_parser
from app.api.admin.schemas import admin_role_schema
from app.base import BaseJWTResource
from app.database import session_scope
from app.datastore import user_datastore
from app.models import Role


@namespace.route("/roles")
class RolesView(BaseJWTResource):
    @namespace.doc("get list of roles")
    @namespace.expect(role_list_parser)
    @namespace.marshal_with(admin_role_schema, as_list=True, code=http.HTTPStatus.OK)
    def get(self):
        args = role_list_parser.parse_args()
        queryset = Role.query.order_by(Role.created_on.asc())
        paginator = queryset.paginate(
            page=args["page"], per_page=args["per_page"], error_out=False
        )

        return paginator.items

    @namespace.doc(
        "create role",
        responses={
            http.HTTPStatus.BAD_REQUEST: "Bad Request",
            http.HTTPStatus.CREATED: "Created",
        },
    )
    @namespace.expect(role_parser)
    @namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.CREATED)
    def post(self):
        new_role = user_datastore.create_role(**role_parser.parse_args())

        try:
            with session_scope() as session:
                session.add(new_role)
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return new_role, http.HTTPStatus.CREATED


@namespace.route("/roles/<int:role_id>")
class SpecificRolesView(BaseJWTResource):
    @namespace.doc(
        "change role",
        responses={
            http.HTTPStatus.NOT_FOUND: "Not Found",
            http.HTTPStatus.BAD_REQUEST: "Bad Request",
        },
    )
    @namespace.expect(role_parser)
    @namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.OK)
    def patch(self, role_id: int):
        role = Role.query.get_or_404(role_id)

        args = role_parser.parse_args()

        if args["name"] in Role.Meta.PROTECTED_ROLE_NAMES:
            raise exceptions.BadRequest("This role is protected.")

        try:
            with session_scope():
                role.update_or_skip(**role_parser.parse_args())
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return role

    @namespace.doc(
        "delete role",
        responses={
            http.HTTPStatus.NOT_FOUND: "Not Found",
            http.HTTPStatus.BAD_REQUEST: "Bad Request",
            http.HTTPStatus.NO_CONTENT: "No Content",
        },
    )
    def delete(self, role_id: int):
        role = Role.query.get_or_404(role_id)

        if role.name in Role.Meta.PROTECTED_ROLE_NAMES:
            raise exceptions.BadRequest("This role is protected.")

        with session_scope() as session:
            session.delete(role)

        return "", http.HTTPStatus.NO_CONTENT
