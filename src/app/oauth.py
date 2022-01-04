from enum import Enum

from authlib.integrations.flask_client import OAuth
from flask import Flask

from app.settings import settings


class OauthNameEnum(str, Enum):
    google = "google"
    yandex = "yandex"


oauth = OAuth()


def yandex_compliance_fix(client, user_data):
    return {
        "sub": user_data["id"],
        "name": user_data["display_name"],
        "email": user_data["default_email"],
    }


oauth.register(
    name=OauthNameEnum.google.value, client_kwargs={"scope": "openid email profile"}
)
oauth.register(
    name=OauthNameEnum.yandex.value,
    authorize_params={
        "response_type": "code",
    },
    userinfo_endpoint=settings.OAUTH.YANDEX_USERINFO_ENDPOINT,
    token_placement="header",
    userinfo_compliance_fix=yandex_compliance_fix,
)


def init_oauth(app: Flask):
    app.config["GOOGLE_CLIENT_ID"] = settings.OAUTH.GOOGLE_CLIENT_ID
    app.config["GOOGLE_CLIENT_SECRET"] = settings.OAUTH.GOOGLE_CLIENT_SECRET
    app.config["GOOGLE_SERVER_METADATA_URL"] = settings.OAUTH.GOOGLE_SERVER_METADATA_URL

    app.config["YANDEX_CLIENT_ID"] = settings.OAUTH.YANDEX_CLIENT_ID
    app.config["YANDEX_CLIENT_SECRET"] = settings.OAUTH.YANDEX_CLIENT_SECRET
    app.config["YANDEX_API_BASE_URL"] = settings.OAUTH.YANDEX_API_BASE_URL
    app.config["YANDEX_ACCESS_TOKEN_URL"] = settings.OAUTH.YANDEX_ACCESS_TOKEN_URL
    app.config["YANDEX_AUTHORIZE_URL"] = settings.OAUTH.YANDEX_AUTHORIZE_URL

    oauth.init_app(app)
