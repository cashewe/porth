import inspect
from enum import Enum
from functools import wraps

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from jsonschema import validate

from ..config_manager import manager

specified_router = APIRouter()


def route_not_found(route: str) -> JSONResponse:
    return JSONResponse(
        content={"route": route, "message": "Route not found"}, status_code=404
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
)


@specified_router.post("/route/{route}", tags=["specified", "mcp"])
@require_route
async def route(
    route: ValidRoute,
    body: dict | None = None,  # not possible to validate this
):
    """Send the body through the specified route."""
    schema = manager.schemas.get(route)
    if schema:
        validate(body, schema)

    return await manager[route].run(body)


@specified_router.post("/rotue/{route}/explain", tags=["specified", "info", "mcp"])
@require_route
async def explain(
    route: ValidRoute,
    body: dict | None = None,
):
    """Explain to the user why their message went a certain way."""
    schema = manager.schemas.get(route)
    if schema:
        validate(body, schema)

    return await manager[route].explain(body)


@specified_router.get("/route/{route}/info", tags=["specified", "info", "mcp"])
@require_route
def info(route: ValidRoute):
    """Full config for the specified route."""
    return {"route": route, "info": manager.info(route)}


@specified_router.get("/route/{route}/readyz", tags=["specified", "health"])
@require_route
async def readyz(route: ValidRoute):
    """Checks status of all tasks in the provided route."""
    results = await manager[route].healthcheck()
    status_code = 200 if all(results) else 503
    return JSONResponse(
        content={
            "route": route,
            "status": "ready" if all(results) else "not ready",
            "breakdown": results,
        },
        status_code=status_code,
    )
