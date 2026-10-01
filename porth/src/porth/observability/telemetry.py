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

from ..settings import settings


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
            "service.name": settings.service_name,
            "service.version": settings.service_version,
            "deployment.environment.name": settings.environment,
            "service.instance.id": settings.otel_service_instance_id,
        }
    )
    tracer_provider = TracerProvider(resource=app_resource)

    traces_endpoint = (
        settings.otel_exporter_otlp_traces_endpoint
        or settings.otel_exporter_otlp_endpoint
    )
    traces_headers = (
        settings.otel_exporter_otlp_traces_headers
        or settings.otel_exporter_otlp_headers
    )
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=traces_endpoint, headers=traces_headers)
    )
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)

    metric_readers = []
    metrics_endpoint = settings.otel_exporter_otlp_metrics_endpoint
    if metrics_endpoint:
        metrics_headers = (
            settings.otel_exporter_otlp_metrics_headers
            or settings.otel_exporter_otlp_headers
        )
        metric_readers.append(
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=metrics_endpoint, headers=metrics_headers)
            )
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
