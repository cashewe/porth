import structlog

from .context import add_observability_context


def configure_logging():
    """configure logging with the right features."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_observability_context,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
    )
