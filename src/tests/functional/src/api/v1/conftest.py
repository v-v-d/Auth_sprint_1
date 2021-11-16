import pytest

from app.services.accounts import AccountsService
from app.services.storages import TokenStorageError


@pytest.fixture
def default_user_jwt_pair(default_user) -> tuple[str, str]:
    account_service = AccountsService(default_user)
    return account_service.get_token_pair()


@pytest.fixture
def default_user_auth_access_header(default_user_jwt_pair) -> dict[str, str]:
    access_token, _ = default_user_jwt_pair
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def default_user_auth_refresh_header(default_user_jwt_pair) -> dict[str, str]:
    _, refresh_token = default_user_jwt_pair
    return {"Authorization": f"Bearer {refresh_token}"}


@pytest.fixture
def failed_account_service_logout(monkeypatch):
    def mocked_return(*args, **kwargs):
        raise TokenStorageError

    monkeypatch.setattr(AccountsService, "logout", mocked_return)
