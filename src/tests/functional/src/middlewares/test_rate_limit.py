import http

import pytest


def test_rate_limit(
    client,
    mocked_rate_limit,
):
    response = client.get(
        path="/api/internal/v1/users/info",
    )

    for i in range(30):
        response = client.get(
            path="/api/internal/v1/users/info",
        )

    assert response.status_code == http.HTTPStatus.TOO_MANY_REQUESTS
