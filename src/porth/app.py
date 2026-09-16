from fastapi import FastAPI

from .observability import (
    configure_logging,
    lifespan,
)
from .routes import (
    core_router,
    specified_router,
)

configure_logging()
app = FastAPI(lifespan=lifespan)
app.include_router(core_router)
app.include_router(specified_router)
