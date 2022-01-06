from contextlib import contextmanager

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, SignallingSession
from sqlalchemy import MetaData, orm

from app.settings import settings
from app.tracing import traced


class TracedSignallingSession(SignallingSession):
    @traced("DB call")
    def execute(self, *args, **kwargs):
        return super().execute(*args, **kwargs)


class TracedSQLAlchemy(SQLAlchemy):
    def create_session(self, options):
        return orm.sessionmaker(class_=TracedSignallingSession, db=self, **options)


metadata = MetaData(schema=settings.DB.SCHEMA)

db = TracedSQLAlchemy(metadata=metadata)
migrate = Migrate()


def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DB.DSN
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""

    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
