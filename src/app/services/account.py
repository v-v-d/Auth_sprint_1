from flask_jwt_extended import create_access_token, create_refresh_token

from app.models import User


class AccountService:
    def __init__(self, user: User):
        self.user = user

    def get_token_pair(self):
        access_token = create_access_token(
            identity=self.user, additional_claims={
                "is_admin": self.user.is_admin,
            }
        )
        refresh_token = create_refresh_token(identity=self.user)

        return access_token, refresh_token
