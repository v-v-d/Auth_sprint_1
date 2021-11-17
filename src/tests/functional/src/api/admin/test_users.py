import http
from uuid import uuid4

import pytest

from app.datastore import user_datastore
from app.models import DefaultRoleEnum


@pytest.fixture
def default_role():
    return user_datastore.find_role(DefaultRoleEnum.staff.value)


def test_check_user_role_true(client, admin_auth_header, default_user):
    user_id = str(default_user.id)
    role_name = DefaultRoleEnum.guest.value

    response = client.get(
        path=f"/admin/users/{user_id}/has-role/{role_name}",
        headers=admin_auth_header,
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json["has_role"]


def test_check_user_role_false(client, admin_auth_header, default_user):
    user_id = str(default_user.id)
    role_name = DefaultRoleEnum.superuser.value

    response = client.get(
        path=f"/admin/users/{user_id}/has-role/{role_name}",
        headers=admin_auth_header,
    )
    assert response.status_code == http.HTTPStatus.OK
    assert not response.json["has_role"]


def test_check_user_role_user_doesnt_exists(client, admin_auth_header):
    user_id = str(uuid4())
    role_name = DefaultRoleEnum.guest.value

    response = client.get(
        path=f"/admin/users/{user_id}/has-role/{role_name}",
        headers=admin_auth_header,
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_change_user_role_ok(client, admin_auth_header, default_user, default_role):
    user_id = str(default_user.id)
    role_id = str(default_role.id)

    response = client.patch(
        path=f"/admin/users/{user_id}/set-role/{role_id}",
        headers=admin_auth_header,
    )

    assert response.status_code == http.HTTPStatus.OK

    user = user_datastore.get_user(default_user.id)
    assert user.has_role(DefaultRoleEnum.staff.value)


def test_change_user_role_user_doesnt_exists(client, admin_auth_header, default_role):
    user_id = str(uuid4())
    role_id = str(default_role.id)

    response = client.patch(
        path=f"/admin/users/{user_id}/set-role/{role_id}",
        headers=admin_auth_header,
    )

    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_change_user_role_role_doesnt_exists(client, admin_auth_header, default_user):
    user_id = str(default_user.id)
    role_id = str(uuid4())

    response = client.patch(
        path=f"/admin/users/{user_id}/set-role/{role_id}",
        headers=admin_auth_header,
    )

    assert response.status_code == http.HTTPStatus.NOT_FOUND
