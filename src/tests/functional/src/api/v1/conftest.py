import pytest

from app.services.accounts import AccountsService
from app.services.storages import TokenStorageError


@pytest.fixture
def failed_account_service_logout(monkeypatch):
    def mocked_return(*args, **kwargs):
        raise TokenStorageError

    monkeypatch.setattr(AccountsService, "logout", mocked_return)
