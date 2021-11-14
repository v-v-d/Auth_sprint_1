from gevent import monkey

monkey.patch_all()

import typer
from IPython import embed
from gevent.pywsgi import WSGIServer

from app.database import session_scope
from app.datastore import user_datastore
from app.main import app
from app.models import DefaultRoleEnum
from app.settings import settings

typer_app = typer.Typer()


@typer_app.command()
def shell():
    embed()


@typer_app.command()
def runserver():
    http_server = WSGIServer((settings.WSGI.HOST, settings.WSGI.PORT), app)
    http_server.serve_forever()


@typer_app.command()
def create_superuser():
    with session_scope():
        user = user_datastore.create_user(
            login=settings.ADMIN_LOGIN,
            password=settings.ADMIN_PASSWORD,
        )
        user_datastore.add_role_to_user(user, DefaultRoleEnum.superuser.value)


if __name__ == "__main__":
    typer_app()
