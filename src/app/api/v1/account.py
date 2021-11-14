import flask
from flask import request
from flask import jsonify

from flask_restplus import Namespace, Resource, fields

from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt

from app.models import User
from app.database import db
from app.services.auth import auth_user, black_list, check_black_list
from app.api.schemas import auth_schema


namespace = Namespace("api/v1/account", description="Registration API operations")

auth_user_schema = namespace.model("User", auth_schema)


@namespace.route('/register')
class SigUp(Resource):
    @namespace.doc('register')
    @namespace.expect(auth_user_schema)
    def post(self):
        login = request.json.get('login')
        password = request.json.get('password')
        if login is None or password is None:
            return flask.abort(400)
        if User.query.filter_by(login=login).first() is not None:
            return flask.abort(400)
        try:
            user = User(
                login=login,
                password=password
            )
            db.session.add(user)  # пометка, разобрать как убрать
            db.session.commit()
            return jsonify(message='registered successfully')
        except:
            return jsonify(
                message='Failed to register. Check the correctness of the password and user fields'
            )


@namespace.route('/refresh')
class Login(Resource):
    @namespace.doc('refresh')
    @namespace.expect(auth_user_schema)
    def post(self):
        user = User.query.filter_by(login=request.json.get('login')).first()
        if not user or not user.check_password(request.json.get('password')):
            return flask.abort(404)
        token = auth_user(user)
        return jsonify(
            access_token=token.json.get('access_token'),
            refresh_token=token.json.get('refresh_token'),
            message='registered successfully'
        )


@namespace.route('/signin')
class SignIn(Resource):
    @namespace.doc('sign_in')
    @jwt_required()
    def get(self):
        if not check_black_list(get_jwt()["jti"]):
            user = get_jwt_identity()
            return user
        else:
            return jsonify(message='Update the token please')


@namespace.route('/logout')
class Logout(Resource):
    @namespace.doc('logout')
    @jwt_required()
    def delete(self):
        access = get_jwt()["jti"]
        return black_list(access)


@namespace.route('/edit_user')
class EditUser(Resource):
    @namespace.doc('edit_user')
    @namespace.expect(auth_user_schema)
    @jwt_required()
    def put(self):
        identity = get_jwt_identity()
        user = User.query.get_or_404(identity)
        if request.json.get('login'):
            user.login = request.json.get('login')
        if request.json.get('password'):
            user.password = request.json.get('password')

        db.session.commit()
        return jsonify('updated successfully')
