from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.database import db
from app.settings import settings


def init_tracing(app: Flask) -> None:  # pragma: no cover
    if not settings.TRACING.ENABLED:
        return

    set_global_textmap(B3MultiFormat())

    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: settings.TRACING.SERVICE_NAME})
        )
    )
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.TRACING.AGENT_HOST_NAME,
        agent_port=settings.TRACING.AGENT_PORT,
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=db.get_engine(app=app))
    RedisInstrumentor().instrument()
