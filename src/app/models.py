from enum import Enum

from flask_security import UserMixin, RoleMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import db


class DefaultRoleEnum(str, Enum):
    superuser = "superuser"
    staff = "staff"


class MethodsExtensionMixin:
    def update_or_skip(self, **kwargs) -> tuple[db.Model, bool]:
        is_updated = False

        for key, val in kwargs.items():
            current_value = getattr(self, key, None)

            if not current_value or current_value == val:
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

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("users.id"))
    role_id = db.Column("role_id", db.Integer(), db.ForeignKey("roles.id"))


class Role(TimestampMixin, db.Model, RoleMixin, MethodsExtensionMixin):
    __tablename__ = "roles"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

    def __str__(self):
        return self.name

    class Meta:
        PROTECTED_ROLE_NAMES = (
            DefaultRoleEnum.superuser.value,
            DefaultRoleEnum.staff.value,
        )


class User(TimestampMixin, db.Model, UserMixin, MethodsExtensionMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    _password = db.Column("password", db.String(255), nullable=False)
    _is_staff = db.Column("is_staff", db.Boolean(), default=False)
    active = db.Column(db.Boolean())
    _is_superuser = db.Column("is_superuser", db.Boolean(), default=False)
    last_login = db.Column(db.DateTime())
    roles = db.relationship(
        "Role",
        secondary="content.roles_users",
        backref=db.backref("users", lazy="dynamic"),
    )

    def __str__(self) -> str:
        return self.login

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password) -> None:
        self._password = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self._password, password)

    @property
    def is_superuser(self) -> bool:
        return self.has_role(DefaultRoleEnum.superuser.value)

    @is_superuser.setter
    def is_superuser(self, state: bool) -> None:
        self._is_superuser = state

    @property
    def is_staff(self) -> bool:
        return self.has_role(DefaultRoleEnum.staff.value)

    @is_staff.setter
    def is_staff(self, state: bool) -> None:
        self._is_staff = state
