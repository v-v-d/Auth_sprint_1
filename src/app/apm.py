from elasticapm.contrib.flask import ElasticAPM
from flask import Flask

from app.settings import settings


def init_apm(app: Flask):
    if not settings.APM.ENABLED:
        return

    ElasticAPM(
        app,
        server_url=settings.APM.SERVER_URL,
        service_name=settings.APM.SERVICE_NAME,
        environment=settings.APM.ENVIRONMENT,
    )
