from logging.config import dictConfig

from flask import Flask

from app.api import init_api
from app.cache import init_cache
from app.database import init_db
from app.datastore import init_datastore
from app.jwt import init_jwt
from app.middlewares import init_middlewares
from app.oauth import init_oauth
from app.settings import settings
from app.settings.logging import LOGGING
from app.tracing import init_tracer

dictConfig(LOGGING)

app = Flask(settings.FLASK_APP)
app.config["DEBUG"] = settings.DEBUG
app.config["SECRET_KEY"] = settings.SECURITY.SECRET_KEY

init_tracer(app)
init_middlewares(app)
init_db(app)
init_datastore(app)
init_oauth(app)
init_api(app)
init_jwt(app)
init_cache(app)

app.app_context().push()
