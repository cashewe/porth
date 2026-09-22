from typing import Any

from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.server.providers.openapi import MCPType, RouteMap
from fastmcp.utilities.lifespan import combine_lifespans
from pydantic import BaseModel, Field

from .config_manager import manager

MCP_MOUNT_PATH = "/mcp"


class AvailableRoute(BaseModel):
    """An available routing target and the input it accepts."""

    name: str = Field(description="Valid route name to pass to routing tools.")
    input_schema: dict[str, Any] | None = Field(
        description="JSON Schema for the route input, or null when unrestricted."
    )


def mount_mcp(app: FastAPI, *, path: str = MCP_MOUNT_PATH) -> FastMCP:
    """Generate and mount an MCP server for the opted-in FastAPI routes."""
    mcp = FastMCP.from_fastapi(
        app=app,
        name="Porth",
        route_maps=[
            RouteMap(tags={"mcp"}, mcp_type=MCPType.TOOL),
            RouteMap(mcp_type=MCPType.EXCLUDE),
        ],
    )

    @mcp.tool(name="list_available_routes")
    def list_available_routes() -> list[AvailableRoute]:
        """List valid route names and their expected input JSON Schemas."""
        return [
            AvailableRoute(
                name=route_name,
                input_schema=manager.schemas.get(route_name),
            )
            for route_name in sorted(manager.keys())
        ]

    mcp_app = mcp.http_app(path="/")

    app.router.lifespan_context = combine_lifespans(
        app.router.lifespan_context,
        mcp_app.lifespan,
    )
    app.mount(path, mcp_app, name="mcp")

    return mcp
