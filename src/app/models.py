from flask_security import UserMixin, RoleMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from app.database import db


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


class Role(TimestampMixin, db.Model, RoleMixin):
    __tablename__ = "roles"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __str__(self):
        return self.name


class User(TimestampMixin, db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    _password = db.Column("password", db.String(255), nullable=False)
    is_staff = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean())
    is_superuser = db.Column(db.Boolean(), default=False)
    last_login = db.Column(db.DateTime())
    roles = db.relationship(
        "Role",
        secondary="content.roles_users",
        backref=db.backref("users", lazy="dynamic"),
    )

    def __str__(self):
        return self.login

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)


class AuthHistory(db.Model):
    __tablename__ = "auth_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_agent = db.Column(db.String(200), nullable=False)
    ip_addr = db.Column(db.String(100), nullable=True)
    device = db.relationship(
        "Device",
        secondary="content.device_users",
        backref=db.backref("users", lazy="dynamic"),
    )


class DeviceAuth(TimestampMixin, db.Model):
    __tablename__ = "device_auth"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __str__(self):
        return self.name
    
    
class DeviceUsers(TimestampMixin, db.Model):
    __tablename__ = "device_users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer(), db.ForeignKey("users.id"))
    device = db.Column("device_id", db.Integer(), db.ForeignKey("device_aut.id"))

    