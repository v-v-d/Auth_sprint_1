import http
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from app.settings import settings


@pytest.fixture(autouse=True)
def enable_tracing(module_mocker: MockerFixture):
    module_mocker.patch.object(settings.TRACING, "ENABLED", True)


def test_tracing_ok(client):
    response = client.get(
        path="/api/internal/v1/users/info",
        headers={settings.TRACING.TRACE_ID_HEADER: uuid4().hex}
    )
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_tracing_failed(client):
    response = client.get(
        path="/api/internal/v1/users/info",
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST
