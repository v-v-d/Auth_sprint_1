from pathlib import Path

import pytest

from app.database import db, session_scope
from app.main import app
from app.settings import settings


assert settings.TESTING, "You must set TESTING=True env for run the tests."

TEST_CONTAINER_SRC_DIR_PATH = Path("/code/tests/functional/testdata/elastic_src")


@pytest.fixture(scope="session", autouse=True)
def db_init():
    with app.app_context():
        db.session.execute("ATTACH DATABASE ':memory:' AS content")
        db.create_all()
        yield
        db.drop_all()


@pytest.fixture(autouse=True)
def clear_db():
    yield
    with session_scope() as session:
        for table in reversed(db.metadata.sorted_tables):
            session.execute(table.delete())
