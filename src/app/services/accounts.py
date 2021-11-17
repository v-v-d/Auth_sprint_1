from datetime import datetime
from uuid import uuid4

from flask_jwt_extended import create_access_token, create_refresh_token

from app.database import session_scope, db
from app.models import User, AuthHistory
from app.services.storages import token_storage, InvalidTokenError


class AccountsServiceError(Exception):
    pass


class AccountsService:
    def __init__(self, user: User):
        self.user = user

    @staticmethod
    def get_authorized_user(login: str, password: str, user_agent, ip_addr) -> User:
        user = User.query.filter_by(login=login).one_or_none()

        if not user or not user.check_password(password):
            raise AccountsServiceError

        if user_agent.platform:
            device = user_agent.platform
        elif user_agent.browser:
            device = user_agent.browser
        else:
            device = user_agent.string

        with session_scope():

            history = AuthHistory(
                user_id=user.id,
                user_agent=user_agent.string,
                ip_addr=ip_addr,
                device=device,
            )
            db.session.add(history)
            user.last_login = datetime.utcnow()  # решил оставить

        return user

    def refresh_token_pair(self, refresh_token_jti: str) -> tuple[str, str]:
        try:
            token_storage.validate_refresh_token(refresh_token_jti, self.user.id)
        except InvalidTokenError:
            token_storage.invalidate_current_refresh_token(self.user.id)
            raise

        return self.get_token_pair()

    def get_token_pair(self) -> tuple[str, str]:
        access_token = create_access_token(
            identity=self.user,
            additional_claims={
                "is_admin": self.user.is_admin,
            },
        )

        refresh_token_jti = str(uuid4())
        refresh_token = create_refresh_token(
            identity=self.user,
            additional_claims={
                "jti": refresh_token_jti,
            },
        )

        token_storage.set_refresh_token(refresh_token_jti, self.user.id)

        return access_token, refresh_token

    @staticmethod
    def logout(access_token_jti: str, user_id: int) -> None:
        token_storage.invalidate_token_pair(access_token_jti, user_id)
