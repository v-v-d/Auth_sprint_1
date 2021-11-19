import http

import pytest


@pytest.fixture
def expected_user_info(default_user):
    return {
        "id": str(default_user.id),
        "login": default_user.login,
        "email": default_user.email,
        "is_active": default_user.is_active,
        "roles": default_user.roles_names_list,
    }


def test_user_info_ok(
    client,
    default_user,
    default_user_auth_access_header,
    expected_user_info,
):
    response = client.get(
        path="/api/internal/v1/users/info",
        headers=default_user_auth_access_header,
    )

    assert response.status_code == http.HTTPStatus.OK
    assert response.json == expected_user_info


def test_user_roles_ok(
    client,
    default_user,
    default_user_auth_access_header,
):
    response = client.get(
        path="/api/internal/v1/users/roles",
        headers=default_user_auth_access_header,
    )

    assert response.status_code == http.HTTPStatus.OK
    assert response.json == [role.name for role in default_user.roles]
