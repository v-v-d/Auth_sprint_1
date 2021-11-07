from app.api.v1.storages import BlackListStorage, RefreshListStorage


def test_adding_token_black_list(redis_init):
    black_list_token = 'as2333asdva2dE232'
    BlackListStorage(redis_init, black_list_token).adding_token_black_list()
