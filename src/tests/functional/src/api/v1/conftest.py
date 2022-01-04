import pytest

from app.services.accounts import AccountsService, AccountsServiceError


@pytest.fixture
def failed_account_service_logout(monkeypatch):
    def mocked_return(*args, **kwargs):
        raise AccountsServiceError

    monkeypatch.setattr(AccountsService, "logout", mocked_return)
