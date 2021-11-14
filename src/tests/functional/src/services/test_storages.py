# import pytest
#
# from app.redis import redis_conn
# from app.services import storages
#
# VALUE = "as2333asdva2dE232.asdasdasd.asdasdasd"
# LOGIN_USER = "Ivanov"
#
#
# @pytest.fixture
# def failed_redis(monkeypatch):
#     def mocked_return(*args, **kwargs):
#         raise Exception
#
#     monkeypatch.setattr(storages.black_list_storage.redis, "set", mocked_return)
#     monkeypatch.setattr(storages.black_list_storage.redis, "get", mocked_return)
#     monkeypatch.setattr(storages.refresh_list_storage.redis, "set", mocked_return)
#     monkeypatch.setattr(storages.refresh_list_storage.redis, "get", mocked_return)
#
#
# def test_add_to_black_list_failed(failed_redis):
#     with pytest.raises(storages.StorageError):
#         storages.black_list_storage.set(VALUE)
#
#
# def test_get_from_black_list_failed(failed_redis):
#     with pytest.raises(storages.StorageError):
#         storages.black_list_storage.get(VALUE)
#
#
# def test_add_to_refresh_token_failed(failed_redis):
#     with pytest.raises(storages.StorageError):
#         storages.refresh_list_storage.set(VALUE)
#
#
# def test_get_from_refresh_token_failed(failed_redis):
#     with pytest.raises(storages.StorageError):
#         storages.refresh_list_storage.get(VALUE)
#
#
# def test_add_token_black_list():
#     storages.black_list_storage.set(VALUE)
#     assert redis_conn.get(VALUE) == ""
#
#
# def test_token_in_black_list():
#     storages.black_list_storage.add(VALUE)
#     assert storages.black_list_storage.exists(VALUE)
#
#
# def test_add_and_get_refresh_token():
#     storages.refresh_list_storage.set(LOGIN_USER, VALUE)
#     assert redis_conn.get(LOGIN_USER) == VALUE
#
#
# def test_build_key():
#     key_black_list = f"{storages.NamespaceEnum.black_list.value}:{VALUE}"
#     assert storages.black_list_storage._build_key(VALUE) == key_black_list
