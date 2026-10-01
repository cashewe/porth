from collections.abc import Awaitable, Callable
from time import perf_counter

import structlog
from starlette.types import Message, Receive, Scope, Send

logger = structlog.get_logger(__name__)

ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


class LoggingMiddleware:
    """Log the lifecycle of each HTTP request as structured events."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]
        status_code: int | None = None
        started_at = perf_counter()

        logger.info("request_started", method=method, path=path)

        async def capture_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, capture_status)
        except Exception:
            logger.exception(
                "request_failed",
                method=method,
                path=path,
                duration_ms=round((perf_counter() - started_at) * 1000, 3),
            )
            raise

        logger.info(
            "request_completed",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round((perf_counter() - started_at) * 1000, 3),
        )
