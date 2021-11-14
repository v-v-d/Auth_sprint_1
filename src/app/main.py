import http
from datetime import timedelta

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, current_user, get_jwt
from flask_restplus import Api, Resource, Namespace, fields
from flask_security import SQLAlchemyUserDatastore, Security
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions

from app.database import init_db, db, session_scope
from app.models import User, Role, DefaultRoleEnum
from app.services.accounts import AccountsService, AccountsServiceError
from app.services.storages import TokenStorageError, InvalidTokenError, token_storage
from app.settings import settings

app = Flask(settings.FLASK_APP)
app.config["DEBUG"] = settings.DEBUG

init_db(app)
# init_api(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()

security.init_app(app, user_datastore)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRES)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRES)
jwt = JWTManager(app)


api = Api(
    title="Auth API",
    version="1.0",
    description="Auth API operations",
)


jwt._set_error_handler_callbacks(api)

admin_namespace = Namespace("admin", path="/admin", description="Admin API operations")
api_namespace = Namespace("auth", path="/api", description="Auth API operations")

api.add_namespace(admin_namespace)
api.add_namespace(api_namespace)


api.init_app(app)


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    try:
        return token_storage.validate_access_token(jwt_payload["jti"])
    except TokenStorageError:
        raise exceptions.FailedDependency()


admin_role_schema = admin_namespace.model("Role", {
    "id": fields.Integer(),
    "name": fields.String(),
    "description": fields.String(),
    "is_active": fields.Boolean(),
})

role_parser = admin_namespace.parser()
role_parser.add_argument("name", type=str, required=True, location="form", help="Role name")
role_parser.add_argument("description", type=str, location="form", help="Role description")

role_list_parser = admin_namespace.parser()
role_list_parser.add_argument("page", type=int, default=0, help="page")
role_list_parser.add_argument(
    "per_page", type=int, default=settings.DEFAULT_PAGE_LIMIT, help="Items per page"
)


login_schema = api_namespace.model("Login", {
    "access_token": fields.String(),
    "refresh_token": fields.String(),
})

signup_schema = api_namespace.model("Signup", {
    "id": fields.Integer(),
    "login": fields.String(),
    "email": fields.String(),
    "is_active": fields.Boolean(),
})

login_parser = api_namespace.parser()
login_parser.add_argument("login", type=str, required=True, location="form", help="Login")
login_parser.add_argument("password", type=str, required=True, location="form", help="Password")

signup_parser = api_namespace.parser()
signup_parser.add_argument("login", type=str, required=True, location="form", help="Login")
signup_parser.add_argument("password", type=str, required=True, location="form", help="Password")
signup_parser.add_argument("email", type=str, location="form", help="Email")  # TODO: add email validation

user_password_parser = api_namespace.parser()
user_password_parser.add_argument("old_password", type=str, required=True, location="form", help="Old password")
user_password_parser.add_argument("new_password", type=str, required=True, location="form", help="New password")


class BaseJWTResource(Resource):
    method_decorators = [] if settings.DEBUG else (jwt_required(), )


@api_namespace.route("/signup")
class SignUpView(Resource):
    @api_namespace.doc("signup")
    @api_namespace.expect(signup_parser)
    @api_namespace.marshal_with(signup_schema, code=http.HTTPStatus.CREATED)
    def post(self):
        try:
            with session_scope():
                new_user = user_datastore.create_user(**signup_parser.parse_args())
                user_datastore.add_role_to_user(new_user, DefaultRoleEnum.guest.value)
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return new_user, http.HTTPStatus.CREATED


@api_namespace.route("/login")
class LoginView(Resource):
    @api_namespace.doc("login")
    @api_namespace.expect(login_parser)
    def post(self):
        args = login_parser.parse_args()

        try:
            user = AccountsService.get_authorized_user(args["login"], args["password"])
        except AccountsServiceError:
            raise exceptions.Unauthorized()

        account_service = AccountsService(user)
        access_token, refresh_token = account_service.get_token_pair()

        return jsonify(access_token=access_token, refresh_token=refresh_token)


@api_namespace.route("/logout")
class LogoutView(BaseJWTResource):
    @api_namespace.doc("logout")
    def post(self):
        try:
            AccountsService.logout(get_jwt()["jti"], current_user.id)
        except TokenStorageError:
            raise exceptions.FailedDependency()


@api_namespace.route("/refresh")
class RefreshView(Resource):
    @api_namespace.doc("refresh")
    @jwt_required(refresh=True)
    def post(self):
        account_service = AccountsService(current_user)

        try:
            access_token, new_refresh_token = account_service.refresh_token_pair(get_jwt()["jti"])
        except TokenStorageError:
            raise exceptions.FailedDependency()
        except InvalidTokenError:
            raise exceptions.Unauthorized()

        return jsonify(access_token=access_token, refresh_token=new_refresh_token)


@api_namespace.route("/users/<int:user_id>/update-password")
class UsersView(BaseJWTResource):
    @api_namespace.doc("update user password")
    @api_namespace.expect(user_password_parser)
    def patch(self, user_id: int):
        args = user_password_parser.parse_args()

        user = User.query.get_or_404(user_id)

        if not user.check_password(args["old_password"]):
            print("bad pwd")
            raise exceptions.BadRequest()

        try:
            with session_scope():
                user.password = args["new_password"]
                AccountsService.logout(get_jwt()["jti"], user.id)
        except TokenStorageError:
            raise exceptions.FailedDependency()


@admin_namespace.route("/roles")
class RolesView(BaseJWTResource):
    @admin_namespace.doc("get list of roles")
    @admin_namespace.expect(role_list_parser)
    @admin_namespace.marshal_with(admin_role_schema, as_list=True, code=http.HTTPStatus.OK)
    def get(self):
        args = role_list_parser.parse_args()
        queryset = Role.query.order_by(Role.created_on.asc())
        paginator = queryset.paginate(
            page=args["page"], per_page=args["per_page"], error_out=False
        )

        return paginator.items

    @admin_namespace.doc("create role", responses={
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
        http.HTTPStatus.CREATED: "Created",
    })
    @admin_namespace.expect(role_parser)
    @admin_namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.CREATED)
    def post(self):
        new_role = user_datastore.create_role(**role_parser.parse_args())

        try:
            with session_scope() as session:
                session.add(new_role)
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return new_role, http.HTTPStatus.CREATED


@admin_namespace.route("/roles/<int:role_id>")
class SpecificRolesView(BaseJWTResource):
    @admin_namespace.doc("change role", responses={
        http.HTTPStatus.NOT_FOUND: "Not Found",
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
    })
    @admin_namespace.expect(role_parser)
    @admin_namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.OK)
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

    @admin_namespace.doc("delete role", responses={
        http.HTTPStatus.NOT_FOUND: "Not Found",
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
        http.HTTPStatus.NO_CONTENT: "No Content",
    })
    def delete(self, role_id: int):
        role = Role.query.get_or_404(role_id)

        if role.name in Role.Meta.PROTECTED_ROLE_NAMES:
            raise exceptions.BadRequest("This role is protected.")

        with session_scope() as session:
            session.delete(role)

        return "", http.HTTPStatus.NO_CONTENT


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


app.app_context().push()
