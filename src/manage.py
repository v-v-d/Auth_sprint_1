from gevent import monkey
monkey.patch_all()

import typer
from IPython import embed
from gevent.pywsgi import WSGIServer

from app.main import app
from app.settings import settings

typer_app = typer.Typer()


@typer_app.command()
def shell():
    embed()


@typer_app.command()
def runserver():
    http_server = WSGIServer((settings.WSGI.HOST, settings.WSGI.PORT), app)
    http_server.serve_forever()


if __name__ == "__main__":
    typer_app()
