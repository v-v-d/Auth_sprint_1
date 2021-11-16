import http
from unittest.mock import ANY

import pytest


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


def test_signup_ok(client, login, password, expected_new_user):
    response = client.post(
        path=f"/api/v1/signup",
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
        path=f"/api/v1/signup",
        data={
            "login": default_user.login,
            "password": password,
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_signup_user_bad_body(client):
    response = client.post(
        path=f"/api/v1/signup",
        data={
            "login": "test",
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST
