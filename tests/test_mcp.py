import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastmcp.client import Client

from porth.config_manager import manager
from porth.mcp import mount_mcp


def build_app(events: list[str] | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if events is not None:
            events.append("started")
        yield
        if events is not None:
            events.append("stopped")

    app = FastAPI(lifespan=lifespan)

    @app.get("/included", tags=["mcp"])
    def included() -> dict[str, bool]:
        return {"included": True}

    @app.get("/excluded", tags=["core"])
    def excluded() -> dict[str, bool]:
        return {"excluded": True}

    return app


def test_mount_mcp_exposes_only_opted_in_routes() -> None:
    app = build_app()
    mcp = mount_mcp(app)

    async def list_tool_names() -> set[str]:
        async with Client(mcp) as client:
            return {tool.name for tool in await client.list_tools()}

    assert asyncio.run(list_tool_names()) == {
        "included_included_get",
        "list_available_routes",
    }


def test_list_available_routes_includes_each_route_schema() -> None:
    mcp = mount_mcp(build_app())

    async def list_routes() -> dict[str, object]:
        async with Client(mcp) as client:
            result = await client.call_tool("list_available_routes", {})
            assert result.structured_content is not None
            return result.structured_content

    routes = asyncio.run(list_routes())

    assert routes == {
        "result": [
            {
                "name": route_name,
                "input_schema": manager.schemas.get(route_name),
            }
            for route_name in sorted(manager.keys())
        ]
    }


def test_mount_mcp_combines_parent_and_mcp_lifespans() -> None:
    events: list[str] = []
    app = build_app(events)
    mount_mcp(app)

    with TestClient(app) as client:
        assert events == ["started"]
        response = client.post(
            "/mcp",
            headers={"Accept": "application/json, text/event-stream"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"},
                },
            },
        )

        assert response.status_code == 200

    assert events == ["started", "stopped"]
