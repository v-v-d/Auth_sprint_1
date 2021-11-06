from flask import Flask

from app.api import init_api
from app.database import init_db
from app.settings import settings

app = Flask(settings.FLASK_APP)

init_db(app)
init_api(app)
