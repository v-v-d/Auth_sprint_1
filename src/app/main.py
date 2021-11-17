from flask import Flask

from app.api import init_api
from app.database import init_db
from app.datastore import init_datastore
from app.jwt import init_jwt
from app.settings import settings

app = Flask(settings.FLASK_APP)
app.config["DEBUG"] = settings.DEBUG

app.config["JWT_SECRET_KEY"] = settings.JWT.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT.JWT_ACCESS_TOKEN_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = settings.JWT.JWT_REFRESH_TOKEN_EXPIRES


init_db(app)
init_datastore(app)
init_api(app)
init_jwt(app)

app.app_context().push()
