import datetime
import http

from flask import Flask, request, Response

from app.api import init_api
from app.cache import init_cache
from app.database import init_db
from app.datastore import init_datastore
from app.jwt import init_jwt
from app.settings import settings
from app.redis import redis_conn


app = Flask(settings.FLASK_APP)
app.config["DEBUG"] = settings.DEBUG


@app.before_request
def rate_limit(*args, **kwargs):
    pipe = redis_conn.pipeline()
    now = datetime.datetime.now()
    key = f"{request.remote_addr}:{now.minute}"

    pipe.incr(key, 1)
    pipe.expire(key, settings.RATE_LIMIT.PERIOD)

    result = pipe.execute()
    request_number = result[0]

    if request_number > settings.RATE_LIMIT.MAX_CALLS:
        return Response(
            'Воу Воу, остановись, отдохни теперь минутку',
            http.HTTPStatus.TOO_MANY_REQUESTS
        )


init_db(app)
init_datastore(app)
init_api(app)
init_jwt(app)
init_cache(app)

app.app_context().push()
