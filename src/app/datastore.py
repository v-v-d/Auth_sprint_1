from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security

from app.database import db
from app.models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()


def init_datastore(app: Flask):
    security.init_app(app, user_datastore)
