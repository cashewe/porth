from fastapi import (
    FastAPI,
    Request,
)
from fastapi.responses import JSONResponse


def configure_exception_handling(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    def generic_handler(request: Request, exc: Exception):
        """Obfiscate the details of internal errors."""
        correlation_id = getattr(request.state, "correlation_id", None)
        headers = (
            {"X-Correlation-ID": correlation_id} if correlation_id is not None else None
        )
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Error Occured!"},
            headers=headers,
        )
