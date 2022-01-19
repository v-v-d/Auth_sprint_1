from enum import Enum
from typing import Optional
from uuid import uuid4

from flask_security import UserMixin, RoleMixin
from sqlalchemy.dialects.postgresql import UUID, ENUM
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db, session_scope


class DefaultRoleEnum(str, Enum):
    guest = "guest"
    superuser = "superuser"
    staff = "staff"


class PlatformEnum(str, Enum):
    pc = "pc"
    mobile = "mobile"
    tablet = "tablet"


class MethodsExtensionMixin:
    def update_or_skip(self, **kwargs) -> tuple[db.Model, bool]:
        is_updated = False

        for key, val in kwargs.items():
            if not hasattr(self, key) or getattr(self, key, None) == val:
                continue

            setattr(self, key, val)

            if not is_updated:
                is_updated = True

        return self, is_updated


class TimestampMixin:
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )


class RolesUsers(db.Model):
    __tablename__ = "roles_users"

    id = db.Column(db.BigInteger(), primary_key=True)
    user_id = db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("users.id"))
    role_id = db.Column("role_id", UUID(as_uuid=True), db.ForeignKey("roles.id"))


class Role(TimestampMixin, db.Model, RoleMixin, MethodsExtensionMixin):
    __tablename__ = "roles"

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return f"<Role {self.name}>"

    class Meta:
        PROTECTED_ROLE_NAMES = (
            DefaultRoleEnum.guest.value,
            DefaultRoleEnum.superuser.value,
            DefaultRoleEnum.staff.value,
        )


class User(TimestampMixin, db.Model, UserMixin, MethodsExtensionMixin):
    __tablename__ = "users"
    __table_args__ = (db.UniqueConstraint("login", "email", name="login_email_uc"),)

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    login = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    _password = db.Column("password", db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    last_login = db.Column(db.DateTime())
    roles = db.relationship(
        "Role",
        secondary="content.roles_users",
        backref=db.backref("users", lazy="dynamic"),
    )

    def __str__(self) -> str:
        return f"<User {self.login}>"

    @classmethod
    def get_or_create(cls, login: str, email: str) -> Optional["User"]:
        from app.datastore import user_datastore  # circular import

        user = cls.query.filter(
            db.and_(
                cls.login == login,
                cls.email == email,
            )
        ).first()

        if not user:
            with session_scope():
                user = user_datastore.create_user(
                    login=login,
                    email=email,
                    password=str(uuid4()),  # random password, will be changed by user
                )

        return user

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str) -> None:
        self._password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self._password, password)

    @property
    def is_admin(self) -> bool:
        return self.has_role(DefaultRoleEnum.staff.value) or self.has_role(
            DefaultRoleEnum.superuser.value
        )

    @property
    def roles_names_list(self) -> list[str]:
        return [role.name for role in self.roles]


class AuthHistory(TimestampMixin, db.Model):
    """
    Partitioned by src/migrations/versions/custom1_auth_history_partitioning.py
    """

    __tablename__ = "auth_history"
    __table_args__ = (db.PrimaryKeyConstraint("id", "platform"),)

    id = db.Column(UUID(as_uuid=True), default=uuid4, nullable=False)
    user_id = db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_agent = db.Column(db.Text, nullable=False)
    ip_addr = db.Column(db.String(100))
    device = db.Column(db.Text)
    platform = db.Column(
        ENUM(PlatformEnum), nullable=False, server_default=PlatformEnum.pc
    )


class SocialAccount(TimestampMixin, db.Model):
    __tablename__ = "social_accounts"
    __table_args__ = (
        db.UniqueConstraint("social_id", "social_name", name="social_uc"),
    )

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = db.relationship(User, backref=db.backref("social_accounts", lazy=True))

    social_id = db.Column(db.String(255), nullable=False)
    social_name = db.Column(db.String(255), nullable=False)

    def __str__(self) -> str:
        return f"<SocialAccount {self.social_name}:{self.user_id}>"

    @classmethod
    def get_or_create(
        cls, social_id: str, social_name: str, user_name: str, user_email: str
    ) -> "SocialAccount":
        social_acc = cls.query.filter_by(
            social_id=social_id,
            social_name=social_name,
        ).first()

        if not social_acc:
            user = User.get_or_create(user_name, user_email)

            with session_scope() as session:
                social_acc = cls(
                    social_id=social_id,
                    social_name=social_name,
                    user_id=user.id,
                )
                session.add(social_acc)

        return social_acc
