import flask
from flask import request
from flask_restplus import Namespace, Resource, fields

from app.models import User
from app.database import db


namespace = Namespace("api/v1/account", description="Registration API operations")

model_register = namespace.model('sigup', {
    'login': fields.String(required=True),
    'password': fields.String(required=True),
})


@namespace.route('/register')
class SigUp(Resource):
    @namespace.doc(model_register)
    def post(self):
        login = request.json.get('login')
        password = request.json.get('password')
        if login is None or password is None:
            flask.abort(400)
        if User.query.filter_by(login=login).first() is not None:
            flask.abort(400)
        try:
            user = User(
                login=login,
                password=password
            )
            db.session.add(user)
            db.session.commit()
        except:
            return {'message': 'Failed to register. Check the correctness of the password and user fields'}
        return {'message': 'registered successfully'}
