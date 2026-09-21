from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any
from uuid import UUID, uuid4

from opentelemetry import trace
from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import Message, Receive, Scope, Send

from ..observability.context import (
    reset_correlation_id,
    set_correlation_id,
)

CORRELATION_HEADER = "X-Correlation-ID"
CORRELATION_ATTRIBUTE = "porth.correlation_id"

ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


class InvalidCorrelationIdError(ValueError):
    """Raised when a request contains an unusable correlation ID."""


def _header_values(scope: Scope) -> list[str]:
    header_name = CORRELATION_HEADER.lower().encode("ascii")
    return [
        value.decode("latin-1")
        for key, value in scope.get("headers", [])
        if key.lower() == header_name
    ]


def resolve_correlation_id(scope: Scope) -> str:
    """Return a supplied canonical UUID or generate one when it is absent."""
    values = _header_values(scope)
    if not values:
        return str(uuid4())
    if len(values) != 1:
        raise InvalidCorrelationIdError(
            f"{CORRELATION_HEADER} must be supplied at most once"
        )

    try:
        return str(UUID(values[0]))
    except (ValueError, AttributeError) as exc:
        raise InvalidCorrelationIdError(
            f"{CORRELATION_HEADER} must contain a valid UUID"
        ) from exc


def _set_request_state(scope: Scope, correlation_id: str) -> None:
    state: MutableMapping[str, Any] = scope.setdefault("state", {})
    state["correlation_id"] = correlation_id


class CorrelationIdMiddleware:
    """Bind one correlation ID to an HTTP request, span, logs, and response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            correlation_id = resolve_correlation_id(scope)
            validation_error = None
        except InvalidCorrelationIdError as exc:
            correlation_id = str(uuid4())
            validation_error = str(exc)

        _set_request_state(scope, correlation_id)
        token = set_correlation_id(correlation_id)

        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute(CORRELATION_ATTRIBUTE, correlation_id)

        async def send_with_correlation_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers[CORRELATION_HEADER] = correlation_id
            await send(message)

        try:
            if validation_error is not None:
                response = JSONResponse(
                    {"message": validation_error},
                    status_code=400,
                )
                await response(scope, receive, send_with_correlation_id)
                return

            await self.app(scope, receive, send_with_correlation_id)
        finally:
            reset_correlation_id(token)
