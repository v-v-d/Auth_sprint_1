from flask import url_for, request, jsonify
from flask_restplus import Resource
from werkzeug import exceptions

from app.api.v1 import namespace
from app.oauth import oauth
from app.services.oauth import OauthServiceError, OauthService


@namespace.route("/login/<string:social_name>")
class OauthLoginView(Resource):
    @namespace.doc("oauth login")
    def get(self, social_name: str):
        client = oauth.create_client(social_name)

        if not client:
            raise exceptions.NotFound()

        redirect_url = url_for(
            "Api v1_oauth_authorization_view", social_name=social_name, _external=True
        )

        return client.authorize_redirect(redirect_url)


@namespace.route("/auth/<string:social_name>")
class OauthAuthorizationView(Resource):
    @namespace.doc("oauth authorization")
    def get(self, social_name: str):
        client = oauth.create_client(social_name)

        if not client:
            raise exceptions.NotFound()

        token = client.authorize_access_token()
        user_info = token.get("userinfo")

        if not user_info:
            user_info = client.userinfo()

        oauth_service = OauthService(
            social_name,
            user_info["sub"],
            user_info["name"],
            user_info["email"],
        )

        try:
            access_token, refresh_token = oauth_service.login(request)
        except OauthServiceError:
            raise exceptions.Unauthorized()

        return jsonify(access_token=access_token, refresh_token=refresh_token)
