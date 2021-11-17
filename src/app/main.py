from flask import Flask

from app.api import init_api
from app.database import init_db
from app.datastore import init_datastore
from app.jwt import init_jwt
from app.settings import settings

app = Flask(settings.FLASK_APP)
app.config["DEBUG"] = settings.DEBUG

init_db(app)
init_datastore(app)
init_api(app)
init_jwt(app)

app.app_context().push()
