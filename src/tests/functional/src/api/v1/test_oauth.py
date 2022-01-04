import http
from typing import Any

import pytest
from pytest_mock import MockerFixture

from app.api.v1.oauth import oauth
from app.database import session_scope
from app.datastore import user_datastore
from app.models import SocialAccount
from app.oauth import OauthNameEnum, yandex_compliance_fix
from app.services.accounts import AccountsService, AccountsServiceError


@pytest.fixture
def mocked_server_metadata() -> dict[str, Any]:
    return {
        "issuer": "https://accounts.google.com",
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "device_authorization_endpoint": "https://oauth2.googleapis.com/device/code",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
        "revocation_endpoint": "https://oauth2.googleapis.com/revoke",
        "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
        "response_types_supported": [
            "code",
            "token",
            "id_token",
            "code token",
            "code id_token",
            "token id_token",
            "code token id_token",
            "none",
        ],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "email", "profile"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_post",
            "client_secret_basic",
        ],
        "claims_supported": [
            "aud",
            "email",
            "email_verified",
            "exp",
            "family_name",
            "given_name",
            "iat",
            "iss",
            "locale",
            "name",
            "picture",
            "sub",
        ],
        "code_challenge_methods_supported": ["plain", "S256"],
        "grant_types_supported": [
            "authorization_code",
            "refresh_token",
            "urn:ietf:params:oauth:grant-type:device_code",
            "urn:ietf:params:oauth:grant-type:jwt-bearer",
        ],
    }


@pytest.fixture
def mocked_token() -> dict[str, Any]:
    return {
        "access_token": "test.access.token",
        "expires_in": 3599,
        "scope": "https://www.googleapis.com/auth/userinfo.email",
        "token_type": "Bearer",
        "id_token": "fake_token_id",
        "expires_at": 1641333160,
    }


@pytest.fixture
def mocked_user_info(default_user_login, default_user_email) -> dict[str, Any]:
    return {
        "sub": "113780970298889785093",
        "name": default_user_login,
        "given_name": "test",
        "family_name": "test",
        "picture": "https://test-img.com/",
        "email": default_user_email,
        "email_verified": True,
        "locale": "ru",
        "hd": "test.com",
    }


@pytest.fixture(autouse=True)
def mocked_oauth_client(
    mocker: MockerFixture, mocked_server_metadata, mocked_token, mocked_user_info
) -> None:
    mocker.patch.object(
        oauth.framework_client_cls,
        "load_server_metadata",
        return_value=mocked_server_metadata,
    )
    mocker.patch.object(
        oauth.framework_client_cls, "authorize_access_token", return_value=mocked_token
    )
    mocker.patch.object(
        oauth.framework_client_cls, "userinfo", return_value=mocked_user_info
    )


@pytest.fixture
def create_default_user_social_acc(default_user, mocked_user_info) -> None:
    with session_scope() as session:
        for social_name in [e.name for e in OauthNameEnum]:
            social_acc = SocialAccount(
                social_id=mocked_user_info["sub"],
                social_name=social_name,
                user_id=default_user.id,
            )
            session.add(social_acc)


@pytest.fixture
def failed_login(mocker: MockerFixture) -> None:
    mocker.patch.object(AccountsService, "login", side_effect=AccountsServiceError)


@pytest.fixture
def unknown_social_name() -> str:
    unknown_social_name = "unknown"
    assert unknown_social_name not in [e.name for e in OauthNameEnum]

    return unknown_social_name


def test_yandex_compliance_fix():
    input_user_data = {
        "id": "236431256",
        "login": "test",
        "client_id": "435c78992ad142a799bffe1a9b6c42cd",
        "display_name": "test",
        "real_name": "test test",
        "first_name": "test",
        "last_name": "test",
        "sex": "male",
        "default_email": "test@test.ru",
        "emails": ["test@test.ru"],
        "psuid": "x.xxx.xxx.xxx",
    }

    expected = {
        "sub": "236431256",
        "name": "test",
        "email": "test@test.ru",
    }

    result = yandex_compliance_fix(None, input_user_data)

    assert result == expected


@pytest.mark.parametrize("social_name", [e.name for e in OauthNameEnum])
class TestOauthParametrized:
    def test_login_ok(self, client, social_name):
        response = client.get(path=f"/api/v1/login/{social_name}")
        assert response.status_code == http.HTTPStatus.FOUND

    def test_auth_ok_new_user(self, client, social_name, mocked_user_info):
        response = client.get(path=f"/api/v1/auth/{social_name}")

        assert response.status_code == http.HTTPStatus.OK

        result = response.json

        assert "access_token" in result
        assert "refresh_token" in result

        user = user_datastore.find_user(login=mocked_user_info["name"])
        assert user

        social_acc = SocialAccount.query.filter_by(
            user_id=user.id, social_name=social_name
        ).first()
        assert social_acc

    def test_auth_ok_existing_user_no_social_acc(
        self, client, default_user, social_name
    ):
        response = client.get(path=f"/api/v1/auth/{social_name}")

        assert response.status_code == http.HTTPStatus.OK

        result = response.json

        assert "access_token" in result
        assert "refresh_token" in result

        social_acc = SocialAccount.query.filter_by(user_id=default_user.id).first()
        assert social_acc

    def test_auth_ok_existing_user_with_social_acc(
        self, client, create_default_user_social_acc, social_name
    ):
        response = client.get(path=f"/api/v1/auth/{social_name}")

        assert response.status_code == http.HTTPStatus.OK

        result = response.json

        assert "access_token" in result
        assert "refresh_token" in result

    def test_auth_failed_login(self, client, failed_login, social_name):
        response = client.get(path=f"/api/v1/auth/{social_name}")
        assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_login_unknown_social_name(client, unknown_social_name):
    response = client.get(path=f"/api/v1/login/{unknown_social_name}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_auth_unknown_social_name(client, unknown_social_name):
    response = client.get(path=f"/api/v1/auth/{unknown_social_name}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND
