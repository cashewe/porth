import inspect
from enum import Enum
from functools import wraps

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from jsonschema import validate

from ..config_manager import manager
from ..middleware.error_handling import ErrorResponse

specified_router = APIRouter()


def route_not_found(route: str) -> JSONResponse:
    return JSONResponse(
        content=ErrorResponse(message=f"Route {route!r} not found.").model_dump(),
        status_code=404,
    )


def require_route(func):
    """Reject requests for routes that are not registered in the manager."""

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(route: str, *args, **kwargs):
            if route not in manager:
                return route_not_found(route)
            return await func(route, *args, **kwargs)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(route: str, *args, **kwargs):
        if route not in manager:
            return route_not_found(route)
        return func(route, *args, **kwargs)

    return sync_wrapper


ValidRoute = Enum(
    "ValidRoute",
    {name: name for name in manager.keys()},  # noqa: SIM118  # this is not a SIM issue, syntax is misleading
    type=str,
)  # this allows swagger to list valid route names to users.


def _route_name(route: ValidRoute | str) -> str:
    if isinstance(route, Enum):
        return route.value
    return route


async def _run_route(
    route: ValidRoute | str,
    body: dict | None,
    version: int | None = None,
):
    route_name = _route_name(route)
    key = manager.resolve(route_name, version)
    schema = manager.schemas.get(key)
    if schema:
        validate(body, schema)

    return await manager[key].run(body)


async def _explain_route(
    route: ValidRoute | str,
    body: dict | None,
    version: int | None = None,
):
    route_name = _route_name(route)
    key = manager.resolve(route_name, version)
    schema = manager.schemas.get(key)
    if schema:
        validate(body, schema)

    return await manager[key].explain(body)


@specified_router.post("/route/{route}/v{version}", tags=["specified", "mcp"])
@specified_router.post("/route/{route}", tags=["specified", "mcp"])
@require_route
async def route(
    route: ValidRoute,
    body: dict | None = None,  # is it possible to inject pydantic here?
    version: int | None = None,
):
    """Send the body through the selected route version, defaulting to latest."""
    return await _run_route(route, body, version)


@specified_router.post(
    "/route/{route}/v{version}/explain",
    tags=["specified", "info", "mcp"],
)
@specified_router.post("/route/{route}/explain", tags=["specified", "info", "mcp"])
@require_route
async def explain(
    route: ValidRoute,
    body: dict | None = None,
    version: int | None = None,
):
    """Explain the selected route version, defaulting to latest."""
    return await _explain_route(route, body, version)


@specified_router.get(
    "/route/{route}/v{version}/info",
    tags=["specified", "info", "mcp"],
)
@specified_router.get("/route/{route}/info", tags=["specified", "info", "mcp"])
@require_route
def info(route: ValidRoute, version: int | None = None):
    """Return the selected route config, defaulting to latest."""
    route_name = _route_name(route)
    key = manager.resolve(route_name, version)
    return {
        "route": route_name,
        "version": key.major,
        "info": manager.info(route_name, key.major),
    }


async def _readyz(route: str, version: int) -> JSONResponse:
    key = manager.resolve(route, version)
    results = await manager[key].healthcheck()
    status_code = 200 if all(results) else 503
    return JSONResponse(
        content={
            "route": route,
            "version": version,
            "status": "ready" if all(results) else "not ready",
            "breakdown": results,
        },
        status_code=status_code,
    )


@specified_router.get(
    "/route/{route}/v{version}/readyz",
    tags=["specified", "health"],
)
@specified_router.get("/route/{route}/readyz", tags=["specified", "health"])
@require_route
async def readyz(route: ValidRoute, version: int | None = None):
    """Check tasks in the selected route version, defaulting to latest."""
    route_name = _route_name(route)
    key = manager.resolve(route_name, version)
    return await _readyz(route_name, key.major)
