import http

from flask import jsonify, request
from flask_jwt_extended import get_jwt, current_user, jwt_required
from flask_restplus import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug import exceptions

from app.api.base import BaseJWTResource
from app.api.v1 import namespace
from app.api.v1.parsers import signup_parser, login_parser
from app.api.v1.schemas import signup_schema
from app.database import session_scope
from app.datastore import user_datastore
from app.models import DefaultRoleEnum
from app.services.accounts import (
    AccountsService,
    AccountsServiceError,
    BadAuthorizationError,
)
from app.services.storages import TokenStorageError


@namespace.route("/signup")
class SignUpView(Resource):
    @namespace.doc("signup")
    @namespace.expect(signup_parser)
    @namespace.marshal_with(signup_schema, code=http.HTTPStatus.CREATED)
    def post(self):
        try:
            with session_scope():
                new_user = user_datastore.create_user(**signup_parser.parse_args())
                user_datastore.add_role_to_user(new_user, DefaultRoleEnum.guest.value)
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return new_user, http.HTTPStatus.CREATED


@namespace.route("/login")
class LoginView(Resource):
    @namespace.doc("login")
    @namespace.expect(login_parser)
    def post(self):
        args = login_parser.parse_args()

        try:
            user = AccountsService.get_authorized_user(
                args["login"],
                args["password"],
            )
        except AccountsServiceError:
            raise exceptions.Unauthorized()

        account_service = AccountsService(user)

        try:
            access_token, refresh_token = account_service.login(request)
        except AccountsServiceError:
            raise exceptions.Unauthorized()

        return jsonify(access_token=access_token, refresh_token=refresh_token)


@namespace.route("/logout")
class LogoutView(BaseJWTResource):
    @namespace.doc("logout")
    def post(self):
        jti = get_jwt()["jti"]

        try:
            AccountsService.logout(jti, current_user.id)
        except AccountsServiceError:
            raise exceptions.FailedDependency()


@namespace.route("/refresh")
class RefreshView(Resource):
    @namespace.doc("refresh")
    @jwt_required(refresh=True)
    def post(self):
        account_service = AccountsService(current_user)
        jti = get_jwt()["jti"]

        try:
            access_token, new_refresh_token = account_service.refresh_token_pair(jti)
        except TokenStorageError:
            raise exceptions.FailedDependency()
        except BadAuthorizationError:
            raise exceptions.Unauthorized()

        return jsonify(access_token=access_token, refresh_token=new_refresh_token)
