import http
from unittest.mock import ANY
from uuid import uuid4

import pytest

from app.database import session_scope
from app.datastore import user_datastore
from app.models import AuthHistory


@pytest.fixture
def expected_user_history_list():
    return [
        {
            "id": ANY,
            "timestamp": ANY,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "ip_addr": "127.0.0.25",
            "device": "Telefunken",
        },
        {
            "id": ANY,
            "timestamp": ANY,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "ip_addr": "127.0.0.25",
            "device": "Telefunken",
        },
        {
            "id": ANY,
            "timestamp": ANY,
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "ip_addr": "127.0.0.25",
            "device": "Telefunken",
        },
    ]


@pytest.fixture
def random_user():
    with session_scope():
        return user_datastore.create_user(id=uuid4(), login="fake", password="fake")


@pytest.fixture
def create_auth_history(default_user, random_user):
    expected_user_data = [
        {
            "user_id": str(default_user.id),
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "ip_addr": "127.0.0.25",
            "device": "Telefunken",
        }
        for _ in range(1, 4)
    ]
    random_user_data = [
        {
            "user_id": str(random_user.id),
            "user_agent": "Fake user agent",
            "ip_addr": "127.0.0.24",
            "device": "Apple",
        }
        for _ in range(1, 4)
    ]
    with session_scope() as session:
        session.bulk_insert_mappings(AuthHistory, expected_user_data)
        session.bulk_insert_mappings(AuthHistory, random_user_data)


def test_update_password_ok(
    client,
    default_user_password,
    default_user,
    default_user_auth_access_header,
):
    new_password = "changed password"

    response = client.patch(
        path=f"/api/v1/users/update-password",
        headers=default_user_auth_access_header,
        data={
            "old_password": default_user_password,
            "new_password": new_password,
        },
    )

    assert response.status_code == http.HTTPStatus.OK

    user = user_datastore.find_user(id=default_user.id)
    assert user.check_password(new_password)

    response = client.patch(
        path=f"/api/v1/users/update-password",
        headers=default_user_auth_access_header,
        data={
            "old_password": default_user_password,
            "new_password": new_password,
        },
    )

    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_update_user_wrong_old_password(
    client,
    default_user,
    default_user_auth_access_header,
):
    response = client.patch(
        path=f"/api/v1/users/update-password",
        headers=default_user_auth_access_header,
        data={
            "old_password": "wrong_old_password",
            "new_password": "changed password",
        },
    )

    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_update_user_failed_token_storage(
    client,
    default_user_password,
    default_user,
    default_user_auth_access_header,
    failed_account_service_logout,
):
    response = client.patch(
        path=f"/api/v1/users/update-password",
        headers=default_user_auth_access_header,
        data={
            "old_password": default_user_password,
            "new_password": "changed password",
        },
    )

    assert response.status_code == http.HTTPStatus.FAILED_DEPENDENCY

    user = user_datastore.find_user(id=default_user.id)
    assert user.check_password(default_user_password)


def test_user_history_list_ok(
    client,
    default_user_auth_access_header,
    expected_user_history_list,
    create_auth_history,
):
    response = client.get(
        path=f"/api/v1/users/history",
        headers=default_user_auth_access_header,
    )
    assert response.status_code == http.HTTPStatus.OK

    result = response.json
    assert len(result) == len(expected_user_history_list)
    assert result == expected_user_history_list
