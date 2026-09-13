from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .config_manager import manager

app = FastAPI()


@app.get("/healthz")
def healthz():
    """Is the app healthy?"""
    return {"status": "healthy"}


@app.get("/readyz")
def readyz():
    """Is the app ready?"""
    if len(manager) == 0:
        return {"status": "not ready"}
    return {"status": "ready"}


@app.get("/info")
def info():
    """Get app information."""
    return {
        "name": "My App",
        "version": "1.0.0",
        "loaded": manager.info(),
    }


@app.post("/{route}/route")
def route(route: str):
    """Handle a POST request to a specific route."""
    if route in manager:
        return JSONResponse(content={"route": route, "message": "Request received"})
    else:
        return JSONResponse(
            content={"route": route, "message": "Route not found"}, status_code=404
        )
