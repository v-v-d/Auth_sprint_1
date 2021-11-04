from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer  # noqa
from app import app  # noqa

from app.settings import settings  # noqa


http_server = WSGIServer((settings.WSGI.HOST, settings.WSGI.PORT), app)
http_server.serve_forever()
