from typing import Any

import pytest

from app.database import session_scope
from app.datastore import user_datastore
from app.models import DefaultRoleEnum, User
from app.services.accounts import AccountsService


@pytest.fixture
def admin_login() -> str:
    return "admin"


@pytest.fixture
def admin_password() -> str:
    return "password"


@pytest.fixture
def admin_user(admin_login, admin_password) -> User:
    with session_scope():
        user = user_datastore.create_user(login=admin_login, password=admin_password)
        user_datastore.add_role_to_user(user, DefaultRoleEnum.staff.value)

    return user


@pytest.fixture
def admin_jwt_pair(admin_user) -> tuple[str, str]:
    account_service = AccountsService(admin_user)
    return account_service.get_token_pair()


@pytest.fixture
def admin_auth_header(admin_jwt_pair) -> dict[str, Any]:
    access_token, _ = admin_jwt_pair
    return {"Authorization": f"Bearer {access_token}"}
