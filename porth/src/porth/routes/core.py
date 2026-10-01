from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..config_manager import manager
from ..settings import settings

core_router = APIRouter()


@core_router.get("/healthz", tags=["core", "health"])
def healthz():
    """Is the app healthy?"""
    return {"status": "healthy"}


@core_router.get("/readyz", tags=["core", "health"])
def readyz():
    """Is the app ready?"""
    if len(manager) == 0:
        return JSONResponse(content={"status": "not ready"}, status_code=503)
    return {"status": "ready"}


@core_router.get("/info", tags=["core", "info"])
def info():
    """Get app level information, including discovered routes."""
    return {
        "name": settings.service_name,
        "version": settings.service_version,
        "api_version": settings.service_version,
        "api_revision": settings.service_revision,
        "routes_version": settings.routes_version,
        "routes_revision": settings.routes_revision,
        "loaded": manager.info(),
    }
