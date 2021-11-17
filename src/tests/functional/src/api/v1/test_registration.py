from app.models import User
from app.settings import settings


def test_create_user(client):
    create_user = client.post(
        "api/v1/account/register",
        json={"login": "test_user1", "password": "390409fds90hLL"},
    )

    assert create_user.status_code == 200


def test_create_token(client):
    create_token = client.post(
        "api/v1/account/login",
        json={"login": "test_user1", "password": "390409fds90hLL"},
    )

    assert create_token.status_code == 200
    assert create_token.get_json("access_token")
    assert create_token.get_json("refresh_token")
