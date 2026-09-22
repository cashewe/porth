from fastapi import FastAPI

from .mcp import mount_mcp
from .middleware import (
    CorrelationIdMiddleware,
    LoggingMiddleware,
    configure_exception_handling,
)
from .observability import (
    configure_logging,
    configure_telemetry,
    instrument_app,
    telemetry_lifespan,
)
from .routes import (
    core_router,
    specified_router,
)

configure_logging()
telemetry_providers = configure_telemetry()

app = FastAPI(lifespan=telemetry_lifespan(telemetry_providers))
configure_exception_handling(app)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.include_router(core_router)
app.include_router(specified_router)
instrument_app(app, telemetry_providers)
mcp = mount_mcp(app)
