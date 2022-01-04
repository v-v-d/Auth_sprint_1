from flask import Request

from app.models import SocialAccount
from app.services.accounts import AccountsService, AccountsServiceError


class OauthServiceError(Exception):
    pass


class OauthService:
    def __init__(
        self, social_name: str, social_id: str, user_name: str, user_email: str
    ) -> None:
        self.social_name = social_name
        self.social_id = social_id
        self.user_name = user_name
        self.user_email = user_email

    def login(self, request: Request) -> tuple[str, str]:
        social_acc = SocialAccount.get_or_create(
            self.social_id, self.social_name, self.user_name, self.user_email
        )
        account_service = AccountsService(social_acc.user)

        try:
            access_token, refresh_token = account_service.login(request)
        except AccountsServiceError as err:
            raise OauthServiceError from err

        return access_token, refresh_token
