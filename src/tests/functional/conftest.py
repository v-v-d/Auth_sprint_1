import asyncio
from pathlib import Path

import pytest
from orjson import orjson

from app.settings import settings

assert settings.TESTING, "You must set TESTING=True env for run the tests."

TEST_CONTAINER_SRC_DIR_PATH = Path("/code/tests/functional/testdata/elastic_src")


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def load_fixture():
    def load(filename):
        with open(TEST_CONTAINER_SRC_DIR_PATH / filename, encoding="utf-8") as f:
            return orjson.loads(f.read())

    return load


@pytest.fixture
def client():
    # TODO
    pass
