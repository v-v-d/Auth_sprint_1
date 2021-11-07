import redis

from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security


from app.api import init_api
from app.database import init_db, db
from app.models import User, Role
from app.settings import settings

app = Flask(settings.FLASK_APP)
app.config["DEBUG"] = settings.DEBUG

init_db(app)
init_api(app)

redis_conn = redis.StrictRedis(host=settings.REDIS.HOST, port=settings.REDIS.PORT)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()

security.init_app(app, user_datastore)

app.app_context().push()
