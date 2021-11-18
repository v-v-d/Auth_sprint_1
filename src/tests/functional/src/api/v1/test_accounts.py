import http
from copy import deepcopy
from datetime import timedelta
from unittest.mock import ANY

import pytest

from app.datastore import user_datastore
from app.main import app
from app.services.accounts import AccountsService
from app.services.storages import token_storage, TokenStorageError
from app.models import AuthHistory


@pytest.fixture
def login():
    return "test login"


@pytest.fixture
def password():
    return "password"


@pytest.fixture
def expected_new_user(login, password):
    return {
        "id": ANY,
        "login": login,
        "email": None,
        "is_active": True,
    }


@pytest.fixture
def failed_token_storage(monkeypatch):
    def mocked_return(*args, **kwargs):
        raise TokenStorageError

    monkeypatch.setattr(token_storage, "_execute", mocked_return)


@pytest.fixture
def failed_account_service_refresh(monkeypatch):
    def mocked_return(*args, **kwargs):
        raise TokenStorageError

    monkeypatch.setattr(AccountsService, "refresh_token_pair", mocked_return)


@pytest.fixture
def mocked_access_token_expires(monkeypatch):
    copy_config = deepcopy(app.config)
    copy_config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=-1)

    monkeypatch.setattr(app, "config", copy_config)


def test_signup_ok(client, login, password, expected_new_user):
    response = client.post(
        path="/api/v1/signup",
        data={
            "login": login,
            "password": password,
        },
    )

    assert response.status_code == http.HTTPStatus.CREATED

    result = response.json
    assert result == expected_new_user


def test_signup_user_already_exists(client, default_user, password):
    response = client.post(
        path="/api/v1/signup",
        data={
            "login": default_user.login,
            "password": password,
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_signup_user_bad_body(client):
    response = client.post(
        path="/api/v1/signup",
        data={
            "login": "test",
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_login_ok(client, default_user, default_user_login, default_user_password):
    response = client.post(
        path="/api/v1/login",
        data={
            "login": default_user_login,
            "password": default_user_password,
        },
    )

    assert response.status_code == http.HTTPStatus.OK

    result = response.json
    assert "access_token" in result
    assert "refresh_token" in result

    user = user_datastore.find_user(id=default_user.id)
    assert user.last_login is not None

    assert len(token_storage.redis.execute_command("keys *")) > 0

    login_history = AuthHistory.query.filter_by(user_id=user.id).first()
    assert login_history


def test_login_user_doesnt_exists(client):
    response = client.post(
        path="/api/v1/login",
        data={
            "login": "test",
            "password": "test",
        },
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_login_wrong_password(client, default_user, default_user_login):
    response = client.post(
        path="/api/v1/login",
        data={
            "login": default_user_login,
            "password": "wrong password",
        },
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_login_failed_token_storage(
    client,
    default_user,
    default_user_login,
    default_user_password,
    failed_token_storage,
):
    response = client.post(
        path="/api/v1/login",
        data={
            "login": default_user_login,
            "password": default_user_password,
        },
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_logout_ok(client, default_user_auth_access_header):
    response = client.post(
        path="/api/v1/logout",
        headers=default_user_auth_access_header,
    )
    assert response.status_code == http.HTTPStatus.OK


def test_logout_failed_token_storage(
    client, default_user_auth_access_header, failed_account_service_logout
):
    response = client.post(
        path="/api/v1/logout",
        headers=default_user_auth_access_header,
    )
    assert response.status_code == http.HTTPStatus.FAILED_DEPENDENCY


def test_logout_access_token_expired(
    client, mocked_access_token_expires, default_user_auth_access_header
):
    response = client.post(
        path="/api/v1/logout",
        headers=default_user_auth_access_header,
    )

    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
    assert response.json == {"msg": "Token has expired"}


def test_logout_double_logout_with_the_same_access_token(
    client, default_user_auth_access_header
):
    response = client.post(
        path="/api/v1/logout",
        headers=default_user_auth_access_header,
    )
    assert response.status_code == http.HTTPStatus.OK

    response = client.post(
        path="/api/v1/logout",
        headers=default_user_auth_access_header,
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
    assert response.json == {"msg": "Token has been revoked"}


def test_refresh_ok(client, default_user_jwt_pair, default_user_auth_refresh_header):
    response = client.post(
        path="/api/v1/refresh",
        headers=default_user_auth_refresh_header,
    )
    assert response.status_code == http.HTTPStatus.OK

    result = response.json
    assert "access_token" in result
    assert "refresh_token" in result
    assert result != default_user_jwt_pair


def test_refresh_failed_token_storage(
    client, default_user_auth_refresh_header, failed_account_service_refresh
):
    response = client.post(
        path="/api/v1/refresh",
        headers=default_user_auth_refresh_header,
    )
    assert response.status_code == http.HTTPStatus.FAILED_DEPENDENCY


def test_refresh_failed_with_reused_refresh_token(
    client, default_user_auth_refresh_header
):
    response = client.post(
        path="/api/v1/refresh",
        headers=default_user_auth_refresh_header,
    )
    assert response.status_code == http.HTTPStatus.OK

    response = client.post(
        path="/api/v1/refresh",
        headers=default_user_auth_refresh_header,
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED

    response = client.post(
        path="/api/v1/refresh",
        headers=default_user_auth_refresh_header,
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED
