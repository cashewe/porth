from fastapi import APIRouter

from ..config_manager import manager

core_router = APIRouter()


@core_router.get("/healthz", tags=["core", "health"])
def healthz():
    """Is the app healthy?"""
    return {"status": "healthy"}


@core_router.get("/readyz", tags=["core", "health"])
def readyz():
    """Is the app ready?"""
    if len(manager) == 0:
        return {"status": "not ready"}
    return {"status": "ready"}


@core_router.get("/info", tags=["core", "info"])
def info():
    """Get app level information, including discovered routes."""
    return {
        "name": "My App",
        "version": "1.0.0",
        "loaded": manager.info(),
    }
