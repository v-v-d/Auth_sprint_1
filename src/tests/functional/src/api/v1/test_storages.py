import pytest
from app.services import storages

VALUE = "as2333asdva2dE232.asdasdasd.asdasdasd"
LOGIN_USER = "Ivanov"


def test_add_token_add_black_list():
    storages.black_list_storage.add(VALUE)
    assert storages.black_list_storage.get(key=VALUE) == ""


def test_token_in_black_list():
    storages.black_list_storage.add(VALUE)
    assert storages.black_list_storage.check(VALUE)


def test_add_and_get_refresh_token():
    storages.refresh_list_storage.add(LOGIN_USER, VALUE)
    assert storages.refresh_list_storage.get(LOGIN_USER) == VALUE


def test_build_key():
    key_black_list = f"{storages.NamespaceEnum.black_list.value}:{VALUE}"
    key_refresh_list = f"{storages.NamespaceEnum.refresh_list.value}:{LOGIN_USER}"
    assert storages.black_list_storage._build_key(VALUE) == key_black_list
    assert storages.refresh_list_storage._build_key(LOGIN_USER) == key_refresh_list
