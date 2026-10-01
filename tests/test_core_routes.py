from fastapi import FastAPI
from fastapi.testclient import TestClient

from porth.config_manager import manager
from porth.routes.core import core_router
from porth.settings import settings


def test_readyz_returns_service_unavailable_when_no_routes_are_loaded(
    monkeypatch,
) -> None:
    monkeypatch.setattr(manager, "configs", {})
    app = FastAPI()
    app.include_router(core_router)

    response = TestClient(app).get("/readyz")

    assert response.status_code == 503
    assert response.json() == {"status": "not ready"}


def test_info_reports_api_and_route_release_identities(monkeypatch) -> None:
    monkeypatch.setattr(settings, "service_version", "1.2.3")
    monkeypatch.setattr(settings, "service_revision", "api-sha")
    monkeypatch.setattr(settings, "routes_version", "4.5.6")
    monkeypatch.setattr(settings, "routes_revision", "routes-sha")
    app = FastAPI()
    app.include_router(core_router)

    response = TestClient(app).get("/info")

    assert response.status_code == 200
    assert response.json() == {
        "name": settings.service_name,
        "version": "1.2.3",
        "api_version": "1.2.3",
        "api_revision": "api-sha",
        "routes_version": "4.5.6",
        "routes_revision": "routes-sha",
        "loaded": manager.info(),
    }
