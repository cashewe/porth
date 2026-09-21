import os
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI
from opentelemetry import (
    metrics,
    trace,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


@dataclass
class TelemetryProviders:
    tracer: TracerProvider
    meter: MeterProvider


def telemetry_lifespan(providers: TelemetryProviders):
    """Create a lifespan handler that shuts down telemetry providers."""

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield

        providers.tracer.shutdown()
        providers.meter.shutdown()

    return lifespan


def configure_telemetry() -> TelemetryProviders:
    """Configure OTEL for the application."""
    app_resource = Resource.create(
        {
            "service.name": os.getenv("SERVICE_NAME") or "porth",
            "service.version": os.getenv("SERVICE_VERSION") or "0.1.0",
            "deployment.environment.name": os.getenv("ENVIRONMENT") or "local",
            "service.instance.id": os.getenv(
                "OTEL_SERVICE_INSTANCE_ID", "local-instance"
            ),
        }
    )
    tracer_provider = TracerProvider(resource=app_resource)

    span_processor = BatchSpanProcessor(OTLPSpanExporter())
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)

    metric_readers = []
    metrics_endpoint = os.getenv("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT")
    if metrics_endpoint:
        metric_readers.append(
            PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=metrics_endpoint))
        )

    meter_provider = MeterProvider(
        resource=app_resource,
        metric_readers=metric_readers,
    )

    metrics.set_meter_provider(meter_provider)

    return TelemetryProviders(tracer=tracer_provider, meter=meter_provider)


def instrument_app(app: FastAPI, providers: TelemetryProviders) -> None:
    """Instrument the FastAPI app with OpenTelemetry."""
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=providers.tracer,
        meter_provider=providers.meter,
    )

    HTTPXClientInstrumentor().instrument(
        tracer_provider=providers.tracer, meter_provider=providers.meter
    )
