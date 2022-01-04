from app.settings import settings

LOGGING = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default",
            "level": settings.LOG_LEVEL,
        }
    },
    "loggers": {
        "authlib": {
            "handlers": ["wsgi"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
    },
    "root": {"level": settings.LOG_LEVEL, "handlers": ["wsgi"]},
}
