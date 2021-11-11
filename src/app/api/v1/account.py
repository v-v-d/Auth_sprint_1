import flask
from flask import request
from flask_restplus import Namespace, Resource, fields
from flask import jsonify

from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import User
from app.database import db
from app.main import jwt
from app.service.auth import auth_user


namespace = Namespace("api/v1/account", description="Registration API operations")

model_register = namespace.model('sigup', {
    'login': fields.String(required=True),
    'password': fields.String(required=True),
})


@namespace.route('/register')
class SigUp(Resource):
    @namespace.doc('register')
    @namespace.expect(model_register)
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
        except:
            return {'message': 'Failed to register. Check the correctness of the password and user fields'}
        return {'message': 'registered successfully'}


@namespace.route('/login')
class Login(Resource):
    @namespace.doc('login')
    @namespace.expect(model_register)
    def post(self):
        user = User.query.filter_by(login=request.json.get('login')).first()
        if not user or not user.check_password(request.json.get('password')):
            return flask.abort(404)

        auth_user(user)

        return {'message': 'registered successfully'}


@namespace.route("/sigin")
class SigIn(Resource):
    @namespace.doc('sigin')
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200