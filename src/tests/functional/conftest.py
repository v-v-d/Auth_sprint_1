import pytest
from alembic import command
from fakeredis import FakeStrictRedis
from flask_migrate import Config

from app import redis
from app.database import db, session_scope
from app.datastore import user_datastore
from app.main import app
from app.models import Role
from app.services import storages
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


@pytest.fixture(autouse=True)
def mocked_redis(monkeypatch):
    faked_redis = FakeStrictRedis(decode_responses=True)
    monkeypatch.setattr(redis, "redis_conn", faked_redis)
    monkeypatch.setattr(storages, "redis_conn", faked_redis)
    monkeypatch.setattr(storages.token_storage, "redis", faked_redis)
