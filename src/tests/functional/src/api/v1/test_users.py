import http
from uuid import uuid4

from app.datastore import user_datastore


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

