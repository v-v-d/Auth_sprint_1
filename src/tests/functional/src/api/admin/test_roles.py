import http
from unittest.mock import ANY
from uuid import uuid4

import pytest

from app.database import session_scope
from app.datastore import user_datastore
from app.models import DefaultRoleEnum


@pytest.fixture
def expected_roles_list():
    return [
        {
            "id": ANY,
            "name": DefaultRoleEnum.guest.value,
            "is_active": None,
            "description": None,
        },
        {
            "id": ANY,
            "name": DefaultRoleEnum.superuser.value,
            "is_active": None,
            "description": None,
        },
        {
            "id": ANY,
            "name": DefaultRoleEnum.staff.value,
            "is_active": None,
            "description": None,
        },
    ]


@pytest.fixture
def expected_created_role():
    return {
        "id": ANY,
        "name": "test",
        "is_active": None,
        "description": "test",
    }


@pytest.fixture
def existing_role():
    with session_scope():
        return user_datastore.create_role(name="test")


@pytest.fixture
def default_role():
    return user_datastore.find_role(DefaultRoleEnum.guest.value)


def test_list_ok(client, admin_auth_header, expected_roles_list):
    response = client.get(path="/admin/roles", headers=admin_auth_header)
    assert response.status_code == http.HTTPStatus.OK

    result = response.json
    assert len(result) == len(expected_roles_list)
    assert result == expected_roles_list


def test_list_forbidden(client, default_user_auth_access_header):
    response = client.get(path="/admin/roles", headers=default_user_auth_access_header)
    assert response.status_code == http.HTTPStatus.FORBIDDEN


def test_create_ok(client, admin_auth_header, expected_created_role):
    response = client.post(
        path="/admin/roles",
        headers=admin_auth_header,
        data={
            "name": "test",
            "description": "test",
        },
    )

    assert response.status_code == http.HTTPStatus.CREATED
    assert response.json == expected_created_role


def test_create_failed_with_wrong_body(client, admin_auth_header):
    response = client.post(
        path="/admin/roles",
        headers=admin_auth_header,
    )

    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_create_failed_with_already_exists(client, admin_auth_header):
    response = client.post(
        path="/admin/roles",
        headers=admin_auth_header,
        data={
            "name": DefaultRoleEnum.guest.value,
        },
    )

    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_change_ok(client, admin_auth_header, existing_role):
    changed_value = "changed"

    response = client.patch(
        path=f"/admin/roles/{str(existing_role.id)}",
        headers=admin_auth_header,
        data={
            "name": changed_value,
            "description": changed_value,
        },
    )

    assert response.status_code == http.HTTPStatus.OK

    result = response.json
    assert result["name"] == changed_value
    assert result["description"] == changed_value


def test_change_role_doesnt_exists(client, admin_auth_header):
    response = client.patch(
        path=f"/admin/roles/{str(uuid4())}",
        headers=admin_auth_header,
        data={
            "name": "changed",
        },
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_change_failed_because_protected_role(client, admin_auth_header, default_role):
    response = client.patch(
        path=f"/admin/roles/{str(default_role.id)}",
        headers=admin_auth_header,
        data={
            "name": "changed",
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_change_failed_because_already_exists(client, admin_auth_header, existing_role):
    response = client.patch(
        path=f"/admin/roles/{str(existing_role.id)}",
        headers=admin_auth_header,
        data={
            "name": DefaultRoleEnum.guest.value,
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_delete_ok(client, admin_auth_header, existing_role):
    response = client.delete(
        path=f"/admin/roles/{str(existing_role.id)}",
        headers=admin_auth_header,
    )
    assert response.status_code == http.HTTPStatus.NO_CONTENT


def test_delete_failed_because_protected_role(client, admin_auth_header, default_role):
    response = client.delete(
        path=f"/admin/roles/{str(default_role.id)}",
        headers=admin_auth_header,
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_delete_role_doesnt_exists(client, admin_auth_header):
    response = client.delete(
        path=f"/admin/roles/{str(uuid4())}",
        headers=admin_auth_header,
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND
