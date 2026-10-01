from fastapi import (
    FastAPI,
    Request,
)
from fastapi.responses import JSONResponse
from jsonschema.exceptions import ValidationError
from pydantic import BaseModel

from .._errors import RouteVersionNotFoundError


class ErrorResponse(BaseModel):
    """The shared response body for handled errors."""

    message: str


def _response(
    request: Request,
    status_code: int,
    error: ErrorResponse,
) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", None)
    headers = (
        {"X-Correlation-ID": correlation_id} if correlation_id is not None else None
    )
    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(),
        headers=headers,
    )


def configure_exception_handling(app: FastAPI) -> None:
    @app.exception_handler(RouteVersionNotFoundError)
    def route_version_handler(request: Request, exc: RouteVersionNotFoundError):
        """Describe every available version when a requested version is absent."""
        available_versions = ", ".join(
            f"v{version}" for version in exc.available_versions
        )
        return _response(
            request,
            404,
            ErrorResponse(
                message=(
                    f"Route {exc.route!r} does not define v{exc.requested_version}. "
                    f"Available versions: {available_versions}."
                )
            ),
        )

    @app.exception_handler(ValidationError)
    def validation_handler(request: Request, _exc: Exception):
        """Manage validation failures manually, since we cant use pydantic here."""
        return _response(
            request,
            422,
            ErrorResponse(message="Invalid request structure for target endpoint."),
        )

    @app.exception_handler(Exception)
    def generic_handler(request: Request, _exc: Exception):
        """Obfuscate the details of internal errors."""
        return _response(
            request,
            500,
            ErrorResponse(message="Internal error occurred."),
        )
