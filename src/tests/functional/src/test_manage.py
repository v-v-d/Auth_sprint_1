import pytest

from app.datastore import user_datastore
from app.models import User, DefaultRoleEnum
from app.settings import settings
from manage import create_superuser


def test_create_superuser_default_login_and_password():
    create_superuser()
    user = User.query.filter_by(login=settings.DEFAULT_ADMIN_LOGIN).first()

    assert user
    assert user.has_role(DefaultRoleEnum.superuser.value)
    assert user.check_password(settings.DEFAULT_ADMIN_PASSWORD)


def test_create_superuser_passed_login_and_password():
    login = "test_login"
    passwd = "test_passwd"

    create_superuser(login=login, password=passwd)
    user = User.query.filter_by(login=login).first()

    assert user
    assert user.has_role(DefaultRoleEnum.superuser.value)
    assert user.check_password(passwd)


def test_create_superuser_passed_only_login():
    login = "test_login"

    create_superuser(login=login)
    user = User.query.filter_by(login=login).first()

    assert user
    assert user.has_role(DefaultRoleEnum.superuser.value)
    assert user.check_password(settings.DEFAULT_ADMIN_PASSWORD)


def test_create_superuser_passed_only_password():
    passwd = "test_passwd"

    create_superuser(password=passwd)
    user = User.query.filter_by(login=settings.ADMIN_LOGIN).first()

    assert user
    assert user.has_role(DefaultRoleEnum.superuser.value)
    assert user.check_password(passwd)


def test_create_superuser_exists_user():
    login = "test_login"
    passwd = "test_passwd"

    user_datastore.create_user(login=login, password=passwd)

    with pytest.raises(ValueError):
        create_superuser(login=login)
