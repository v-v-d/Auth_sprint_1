from copy import deepcopy

import pytest
from alembic import command
from fakeredis import FakeStrictRedis
from flask_migrate import Config

from app import redis
from app import middlewares
from app.database import db, session_scope
from app.datastore import user_datastore
from app.main import app
from app.models import Role, DefaultRoleEnum
from app.services import storages
from app.services.accounts import AccountsService
from app.settings import settings

assert settings.TESTING, "You must set TESTING=True env for run the tests."


@pytest.fixture(scope="session", autouse=True)
def db_init():
    with app.app_context():
        config = Config("migrations/alembic.ini")
        config.set_main_option("script_location", "migrations")
        command.upgrade(config, "head")

        yield
        command.downgrade(config, "base")


@pytest.fixture(autouse=True)
def clear_db():
    yield
    with session_scope() as session:
        for table in reversed(db.metadata.sorted_tables):
            session.execute(table.delete())

        for role in Role.Meta.PROTECTED_ROLE_NAMES:
            user_datastore.create_role(name=role)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def default_user_login():
    return "test"


@pytest.fixture
def default_user_email():
    return "test@test.com"


@pytest.fixture
def default_user_password():
    return "test"


@pytest.fixture
def default_user(default_user_login, default_user_password, default_user_email):
    with session_scope():
        user = user_datastore.create_user(
            login=default_user_login,
            password=default_user_password,
            email=default_user_email,
        )
        user_datastore.add_role_to_user(user, DefaultRoleEnum.guest.value)

    return user


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


@pytest.fixture(autouse=True)
def mocked_redis(monkeypatch):
    faked_redis = FakeStrictRedis(decode_responses=True)
    monkeypatch.setattr(redis, "redis_conn", faked_redis)
    monkeypatch.setattr(storages, "redis_conn", faked_redis)
    monkeypatch.setattr(storages.token_storage, "redis", faked_redis)
    monkeypatch.setattr(middlewares, "redis_conn", faked_redis)


@pytest.fixture(autouse=True)
def mocked_cache(monkeypatch):
    copy_config = deepcopy(app.config)
    copy_config["CACHE_TYPE"] = "SimpleCache"
    del copy_config["CACHE_REDIS_URL"]

    monkeypatch.setattr(app, "config", copy_config)


@pytest.fixture
def mocked_rate_limit(monkeypatch):
    monkeypatch.setattr(settings.RATE_LIMIT, "MAX_CALLS", 4)
