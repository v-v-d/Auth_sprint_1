import http

from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions

from app.api.parsers import role_parser
from flask import Flask
from flask_jwt_extended import JWTManager, jwt_required
from flask_restplus import Api, Resource, Namespace
from flask_security import SQLAlchemyUserDatastore, Security


from app.api import init_api
from app.api.admin.utils import admin_role_required
from app.api.schemas import role_schema
from app.database import init_db, db, session_scope
from app.models import User, Role
from app.settings import settings

app = Flask(settings.FLASK_APP)
app.config["DEBUG"] = settings.DEBUG

init_db(app)
# init_api(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()

security.init_app(app, user_datastore)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)


api = Api(
    title="Auth API",
    version="1.0",
    description="Auth API operations",
)

namespace = Namespace("admin", path="/admin", description="Auth admin API")
api_namespace = Namespace("auth", path="/api", description="Auth API operations")

api.add_namespace(namespace)
api.add_namespace(api_namespace)


api.init_app(app)

admin_role_schema = namespace.model("Role", role_schema)


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


class BaseJWTResource(Resource):
    method_decorators = (jwt_required(), )


class BaseJWTAdminResource(Resource):
    pass
    # method_decorators = (admin_role_required, jwt_required())


@namespace.route("/login")
class LoginView(BaseJWTResource):
    @namespace.doc("login")
    @namespace.expect(role_parser)
    @namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.CREATED)
    def post(self):
        new_role = Role(**role_parser.parse_args())

        try:
            with session_scope() as session:
                session.add(new_role)
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return new_role, http.HTTPStatus.CREATED


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username).one_or_none()
    if not user or not user.check_password(password):
        return jsonify("Wrong username or password"), 401

    # Notice that we are passing in the actual sqlalchemy user object here
    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token)


@app.route("/who_am_i", methods=["GET"])
@jwt_required()
def protected():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(
        id=current_user.id,
        full_name=current_user.full_name,
        username=current_user.username,
    )


@namespace.route("/roles")
class RolesView(BaseJWTAdminResource):
    @namespace.doc("get list of roles")
    @namespace.marshal_with(admin_role_schema, as_list=True, code=http.HTTPStatus.OK)
    def get(self):
        return Role.query.all()

    @namespace.doc("create role", responses={
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
        http.HTTPStatus.CREATED: "Created",
    })
    @namespace.expect(role_parser)
    @namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.CREATED)
    def post(self):
        new_role = Role(**role_parser.parse_args())

        try:
            with session_scope() as session:
                session.add(new_role)
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return new_role, http.HTTPStatus.CREATED


@namespace.route("/roles/<int:role_id>")
class SpecificRolesView(BaseJWTAdminResource):
    @namespace.doc("change role", responses={
        http.HTTPStatus.NOT_FOUND: "Not Found",
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
    })
    @namespace.expect(role_parser)
    @namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.OK)
    def patch(self, role_id: int):
        role = Role.query.get_or_404(id=role_id)

        args = role_parser.parse_args()

        if args["name"] in Role.Meta.PROTECTED_ROLE_NAMES:
            raise exceptions.BadRequest("This role is protected.")

        try:
            with session_scope():
                role.update_or_skip(**role_parser.parse_args())
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return role

    @namespace.doc("delete role", responses={
        http.HTTPStatus.NOT_FOUND: "Not Found",
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
        http.HTTPStatus.NO_CONTENT: "No Content",
    })
    @namespace.marshal_with("", code=http.HTTPStatus.NO_CONTENT)
    def delete(self, role_id: int):
        role = Role.query.get_or_404(id=role_id)

        args = role_parser.parse_args()

        if args["name"] in Role.Meta.PROTECTED_ROLE_NAMES:
            raise exceptions.BadRequest("This role is protected.")

        with session_scope():
            role.is_active = False

        return "", http.HTTPStatus.NO_CONTENT


app.app_context().push()
