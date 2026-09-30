import asyncio
import json

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from porth.middleware.error_handling import configure_exception_handling
from porth.routes.specified import require_route, specified_router


def test_require_route_returns_404_for_missing_route():
    @require_route
    async def sample(route: str):
        return {"route": route, "ok": True}

    response = asyncio.run(sample("missing"))

    assert response.status_code == 404
    assert json.loads(response.body) == {"message": "Route 'missing' not found."}


def test_version_not_found_response_lists_available_versions():
    app = FastAPI()
    configure_exception_handling(app)
    app.include_router(specified_router)

    response = TestClient(app).get("/route/example-1/v3/info")

    assert response.status_code == 404
    assert response.json() == {
        "message": (
            "Route 'example-1' does not define v3. Available versions: v1, v2."
        ),
    }


def test_schema_validation_uses_shared_error_response():
    app = FastAPI()
    configure_exception_handling(app)
    app.include_router(specified_router)

    response = TestClient(app).post("/route/example-2", json={})

    assert response.status_code == 422
    assert response.json() == {
        "message": "Invalid request structure for target endpoint."
    }


def test_unversioned_info_identifies_resolved_version():
    app = FastAPI()
    configure_exception_handling(app)
    app.include_router(specified_router)

    response = TestClient(app).get("/route/example-1/info")

    assert response.status_code == 200
    assert response.json()["version"] == 2


def test_explicit_version_info_resolves_that_version():
    app = FastAPI()
    configure_exception_handling(app)
    app.include_router(specified_router)

    response = TestClient(app).get("/route/example-1/v1/info")

    assert response.status_code == 200
    assert response.json()["version"] == 1


def test_raw_and_versioned_paths_share_endpoint_functions():
    endpoints = {
        route.path: route.endpoint
        for route in specified_router.routes
        if isinstance(route, APIRoute)
    }

    assert endpoints["/route/{route}"] is endpoints["/route/{route}/v{version}"]
    assert (
        endpoints["/route/{route}/explain"]
        is endpoints["/route/{route}/v{version}/explain"]
    )
    assert (
        endpoints["/route/{route}/info"] is endpoints["/route/{route}/v{version}/info"]
    )
    assert (
        endpoints["/route/{route}/readyz"]
        is endpoints["/route/{route}/v{version}/readyz"]
    )
