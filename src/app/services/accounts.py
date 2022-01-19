from datetime import datetime
from uuid import uuid4

from flask import Request
from flask_jwt_extended import create_access_token, create_refresh_token
from user_agents import parse

from app.database import session_scope, db
from app.models import User, AuthHistory, PlatformEnum
from app.services.storages import (
    token_storage,
    InvalidTokenError,
    TokenStorageError,
)


class BaseAccountsServiceError(Exception):
    pass


class AccountsServiceError(BaseAccountsServiceError):
    pass


class BadAuthorizationError(BaseAccountsServiceError):
    pass


class MissedPlatformError(AccountsServiceError):
    pass


class AccountsService:
    def __init__(self, user: User):
        self.user = user

    def login(self, request: Request) -> tuple[str, str]:
        self.record_entry_time(request)

        try:
            access_token, refresh_token = self.get_token_pair()
        except TokenStorageError as err:
            raise AccountsServiceError from err

        with session_scope():
            self.user.last_login = datetime.utcnow()

        return access_token, refresh_token

    @staticmethod
    def get_authorized_user(login: str, password: str) -> User:
        user = User.query.filter_by(login=login).one_or_none()

        if not user or not user.check_password(password):
            raise AccountsServiceError

        return user

    def refresh_token_pair(self, refresh_token_jti: str) -> tuple[str, str]:
        try:
            token_storage.validate_refresh_token(refresh_token_jti, self.user.id)
        except InvalidTokenError as err:
            token_storage.invalidate_current_refresh_token(self.user.id)
            raise BadAuthorizationError from err

        return self.get_token_pair()

    def get_token_pair(self) -> tuple[str, str]:
        access_token = create_access_token(
            identity=self.user,
            additional_claims={
                "is_admin": self.user.is_admin,
                "roles": self.user.roles_names_list,
            },
        )

        refresh_token_jti = str(uuid4())
        refresh_token = create_refresh_token(
            identity=self.user,
            additional_claims={
                "jti": refresh_token_jti,
            },
        )

        try:
            token_storage.set_refresh_token(refresh_token_jti, self.user.id)
        except TokenStorageError as err:
            raise AccountsServiceError from err

        return access_token, refresh_token

    def record_entry_time(self, request: Request) -> None:
        user_agent = parse(request.user_agent.string)

        platform = PlatformEnum.pc

        if user_agent.is_mobile:
            platform = PlatformEnum.mobile
        elif user_agent.is_tablet:
            platform = PlatformEnum.tablet

        with session_scope():
            history = AuthHistory(
                user_id=self.user.id,
                user_agent=request.user_agent.string,
                ip_addr=request.remote_addr,
                device=user_agent.device,
                platform=platform,
            )
            db.session.add(history)

    @staticmethod
    def logout(access_token_jti: str, user_id: int) -> None:
        try:
            token_storage.invalidate_token_pair(access_token_jti, user_id)
        except TokenStorageError as err:
            raise AccountsServiceError from err
