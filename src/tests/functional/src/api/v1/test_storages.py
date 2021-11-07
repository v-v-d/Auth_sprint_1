import pytest
from app.services.storages import BlackListStorage, RefreshListStorage
from app.redis import redis_conn


def test_token_in_black_list():
    black_list_token = 'as2333asdva2dE232'
    BlackListStorage(redis_conn).add(black_list_token)
    assert BlackListStorage(redis_conn).get_token(black_list_token) == True
