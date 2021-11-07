import pytest
from app.services import storages

VALUE = "as2333asdva2dE232.asdasdasd.asdasdasd"


def test_token_in_black_list():
    storages.black_list_token.add(VALUE)
    assert storages.black_list_token.check(VALUE)


def test_refresh_token():
    login_user = "Ivanov"
    storages.refresh_list_token.add(VALUE, login_user)
    assert storages.refresh_list_token.get_refresh_token(login_user) == VALUE
