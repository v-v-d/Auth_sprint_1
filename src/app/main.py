from flask import Flask

from app.api import init_api
from app.database import init_db

app = Flask(__name__)

init_db(app)
init_api(app)
