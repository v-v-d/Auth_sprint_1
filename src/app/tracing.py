from functools import wraps
from typing import Callable, Iterable, Any

from flask import Flask
from flask_opentracing import FlaskTracer
from jaeger_client import Config

from app.settings import settings

JAEGER_CONFIG = {
    "sampler": {
        "type": settings.JAEGER.TYPE,
        "param": 1,
    },
    "local_agent": {
        "reporting_host": settings.JAEGER.REPORTING_HOST,
        "reporting_port": settings.JAEGER.REPORTING_PORT,
    },
    "logging": True,
    "trace_id_header": settings.JAEGER.TRACE_ID_HEADER,
}

tracer = None

if settings.JAEGER.ENABLED:
    config = Config(
        config=JAEGER_CONFIG,
        service_name=settings.JAEGER.SERVICE_NAME,
        validate=True,
    )
    tracer = config.initialize_tracer()


def init_tracer(app: Flask) -> None:
    if settings.JAEGER.ENABLED:
        FlaskTracer(tracer=tracer, trace_all_requests=True, app=app)


def traced(span_name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Iterable, **kwargs: dict[str, Any]) -> Any:
            if settings.JAEGER.ENABLED:
                with tracer.start_active_span(span_name):
                    return func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
