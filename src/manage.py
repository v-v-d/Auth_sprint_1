from gevent import monkey

monkey.patch_all()

from typing import Optional

import typer
from IPython import embed
from gevent.pywsgi import WSGIServer
from sqlalchemy.exc import IntegrityError

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
    http_server = WSGIServer(
        (settings.WSGI.HOST, settings.WSGI.PORT), app, spawn=settings.WSGI.workers
    )
    http_server.serve_forever()


@typer_app.command()
def create_superuser(
    login: Optional[str] = typer.Option(None),
    password: Optional[str] = typer.Option(None),
) -> None:
    if not login:
        login = settings.SECURITY.DEFAULT_ADMIN_LOGIN

    if not password:
        password = settings.SECURITY.DEFAULT_ADMIN_PASSWORD

    try:
        with session_scope():
            user = user_datastore.create_user(login=login, password=password)
            user_datastore.add_role_to_user(user, DefaultRoleEnum.superuser.value)
    except IntegrityError:
        raise ValueError(
            f"Failed to create superuser! User with login {login} already exists.",
        )


if __name__ == "__main__":
    typer_app()
