import json
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import SpanKind

from porth.middleware import (
    CorrelationIdMiddleware,
    LoggingMiddleware,
    configure_exception_handling,
)
from porth.observability.context import get_correlation_id
from porth.observability.logger import configure_logging

HEADER = "X-Correlation-ID"


def build_app() -> FastAPI:
    app = FastAPI()
    configure_exception_handling(app)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/{path:path}")
    def endpoint(path: str):
        if path == "error":
            raise RuntimeError("boom")
        return {
            "path": path,
            "correlation_id": get_correlation_id(),
        }

    return app


def test_missing_correlation_id_is_generated() -> None:
    with TestClient(build_app()) as client:
        response = client.get("/info")

    correlation_id = response.headers[HEADER]
    parsed = UUID(correlation_id)

    assert parsed.version == 4
    assert response.json()["correlation_id"] == correlation_id


def test_supplied_correlation_id_is_preserved() -> None:
    correlation_id = str(uuid4())

    with TestClient(build_app()) as client:
        response = client.get("/info", headers={HEADER: correlation_id})

    assert response.headers[HEADER] == correlation_id
    assert response.json()["correlation_id"] == correlation_id


def test_health_endpoints_receive_correlation_ids() -> None:
    with TestClient(build_app()) as client:
        health_response = client.get("/healthz")
        ready_response = client.get("/readyz")

    UUID(health_response.headers[HEADER])
    UUID(ready_response.headers[HEADER])


def test_invalid_correlation_id_is_rejected_with_a_new_id() -> None:
    with TestClient(build_app()) as client:
        response = client.get("/info", headers={HEADER: "not-a-uuid"})

    assert response.status_code == 400
    UUID(response.headers[HEADER])
    assert response.json() == {"message": "X-Correlation-ID must contain a valid UUID"}


def test_unhandled_error_response_includes_correlation_id() -> None:
    correlation_id = str(uuid4())

    with TestClient(build_app(), raise_server_exceptions=False) as client:
        response = client.get("/error", headers={HEADER: correlation_id})

    assert response.status_code == 500
    assert response.headers[HEADER] == correlation_id


def test_request_logs_share_the_correlation_id(capsys) -> None:
    configure_logging()
    correlation_id = str(uuid4())

    with TestClient(build_app()) as client:
        client.get("/info", headers={HEADER: correlation_id})

    events = [
        json.loads(line)
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("{")
    ]
    request_events = [
        event
        for event in events
        if event["event"] in {"request_started", "request_completed"}
    ]

    assert len(request_events) == 2
    assert all(event["correlation_id"] == correlation_id for event in request_events)


def test_server_span_contains_the_correlation_id() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    test_app = build_app()
    FastAPIInstrumentor.instrument_app(test_app, tracer_provider=provider)

    with TestClient(test_app) as client:
        response = client.get("/info")

    server_span = next(
        span for span in exporter.get_finished_spans() if span.kind is SpanKind.SERVER
    )
    attributes = server_span.attributes

    assert attributes is not None
    assert attributes["porth.correlation_id"] == response.headers[HEADER]
    provider.shutdown()


def test_correlation_context_is_cleared_after_request() -> None:
    with TestClient(build_app()) as client:
        client.get("/info")

    assert get_correlation_id() is None
