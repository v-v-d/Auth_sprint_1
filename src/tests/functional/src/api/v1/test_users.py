import http
import pytest
from uuid import uuid4

from unittest.mock import ANY

from app.datastore import user_datastore


@pytest.fixture
def expected_user_history_list(default_user):
    return [
        {
            "id": ANY,
            "user_id": str(default_user.id),
            "user_agent": "curl/",
            "ip_addr": "127.0.0.25",
            "device": "Telefunken",
        },
        {
            "id": ANY,
            "user_id": str(default_user.id),
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
            "ip_addr": "127.0.0.1",
            "device": "apple",
        },
        {
            "id": ANY,
            "user_id": str(default_user.id),
            "user_agent": "curl/",
            "ip_addr": "127.0.0.25",
            "device": "Telefunken",
        },
    ]


def test_update_password_ok(
    client,
    default_user_password,
    default_user,
    default_user_auth_access_header,
):
    user_id = str(default_user.id)
    new_password = "changed password"

    response = client.patch(
        path=f"/api/v1/users/{user_id}/update-password",
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
        path=f"/api/v1/users/{user_id}/update-password",
        headers=default_user_auth_access_header,
        data={
            "old_password": default_user_password,
            "new_password": new_password,
        },
    )

    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_update_user_doesnt_exists(
    client,
    default_user_password,
    default_user,
    default_user_auth_access_header,
):
    user_id = str(uuid4())

    response = client.patch(
        path=f"/api/v1/users/{user_id}/update-password",
        headers=default_user_auth_access_header,
        data={
            "old_password": default_user_password,
            "new_password": "changed password",
        },
    )

    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_update_user_wrong_old_password(
    client,
    default_user,
    default_user_auth_access_header,
):
    user_id = str(default_user.id)

    response = client.patch(
        path=f"/api/v1/users/{user_id}/update-password",
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
    user_id = str(default_user.id)

    response = client.patch(
        path=f"/api/v1/users/{user_id}/update-password",
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
    default_user,
    default_user_password,
    default_user_auth_access_header,
    expected_user_history_list,
):
    response = client.get(
        path=f"/api/v1/users/{default_user.id}/history",
        headers=default_user_auth_access_header,
    )
    assert response.status_code == http.HTTPStatus.OK
    #
    # result = response.json
    # assert len(result) == len(expected_user_history_list)
    # assert result == expected_user_history_list
