from typer.testing import CliRunner

from app.models import User, DefaultRoleEnum
from app.settings import settings
from manage import typer_app

runner = CliRunner()


def test_create_superuser_default_login_and_password():
    result = runner.invoke(typer_app, ["create-superuser"])
    assert result.exit_code == 0

    user = User.query.filter_by(login=settings.SECURITY.DEFAULT_ADMIN_LOGIN).first()

    assert user
    assert user.has_role(DefaultRoleEnum.superuser.value)
    assert user.check_password(settings.SECURITY.DEFAULT_ADMIN_PASSWORD)


def test_create_superuser_passed_login_and_password():
    login = "test_login"
    passwd = "test_passwd"

    result = runner.invoke(
        typer_app, ["create-superuser", "--login", login, "--password", passwd]
    )
    assert result.exit_code == 0

    user = User.query.filter_by(login=login).first()

    assert user
    assert user.has_role(DefaultRoleEnum.superuser.value)
    assert user.check_password(passwd)


def test_create_superuser_passed_only_login():
    login = "test_login"

    result = runner.invoke(typer_app, ["create-superuser", "--login", login])
    assert result.exit_code == 0

    user = User.query.filter_by(login=login).first()

    assert user
    assert user.has_role(DefaultRoleEnum.superuser.value)
    assert user.check_password(settings.SECURITY.DEFAULT_ADMIN_PASSWORD)


def test_create_superuser_passed_only_password():
    passwd = "test_passwd"

    result = runner.invoke(typer_app, ["create-superuser", "--password", passwd])
    assert result.exit_code == 0

    user = User.query.filter_by(login=settings.SECURITY.DEFAULT_ADMIN_LOGIN).first()

    assert user
    assert user.has_role(DefaultRoleEnum.superuser.value)
    assert user.check_password(passwd)


def test_create_superuser_exists_user():
    login = "test_login"
    passwd = "test_passwd"

    result = runner.invoke(
        typer_app, ["create-superuser", "--login", login, "--password", passwd]
    )
    assert result.exit_code == 0

    result = runner.invoke(
        typer_app, ["create-superuser", "--login", login, "--password", passwd]
    )
    assert result.exit_code != 0
