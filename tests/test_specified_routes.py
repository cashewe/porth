import asyncio

from porth.routes.specified import require_route


def test_require_route_returns_404_for_missing_route():
    @require_route
    async def sample(route: str):
        return {"route": route, "ok": True}

    response = asyncio.run(sample("missing"))

    assert response.status_code == 404
    assert b'"message":"Route not found"' in response.body
