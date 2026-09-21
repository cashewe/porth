from collections.abc import MutableMapping
from contextvars import ContextVar, Token
from typing import Any

from opentelemetry import trace

_correlation_id: ContextVar[str | None] = ContextVar(
    "correlation_id",
    default=None,
)


def get_correlation_id() -> str | None:
    """Return the correlation ID bound to the current request."""
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> Token[str | None]:
    """Bind a correlation ID and return a token for restoring the context."""
    return _correlation_id.set(correlation_id)


def reset_correlation_id(token: Token[str | None]) -> None:
    """Restore the correlation context that preceded the current request."""
    _correlation_id.reset(token)


def add_observability_context(
    _logger: Any,
    _method_name: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Add request and OpenTelemetry identifiers to a structured log event."""
    correlation_id = get_correlation_id()
    if correlation_id is not None:
        event_dict["correlation_id"] = correlation_id

    span_context = trace.get_current_span().get_span_context()
    if span_context.is_valid:
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")

    return event_dict
