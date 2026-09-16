# needs correlation id, and otel span ids
import logging  # noqa: F401 # structlog examples import this unused?

import structlog


def configure_logging():
    """configure logging with the right features."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
    )
