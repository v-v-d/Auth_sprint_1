from datetime import timedelta

from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security

from flask_jwt_extended import JWTManager

from app.api import init_api
from app.database import init_db, db
from app.models import User, Role
from app.settings import settings

app = Flask(settings.FLASK_APP)
app.config["DEBUG"] = settings.DEBUG
app.config["JWT_SECRET_KEY"] = settings.JWT.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT.JWT_ACCESS_TOKEN_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = settings.JWT.JWT_REFRESH_TOKEN_EXPIRES


init_db(app)
init_api(app)
JWTManager(app)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()

security.init_app(app, user_datastore)

app.app_context().push()
