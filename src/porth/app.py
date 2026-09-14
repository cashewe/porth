from fastapi import FastAPI

from .observability import (
    lifespan,
)
from .routes import (
    core_router,
    specified_router,
)

app = FastAPI(lifespan=lifespan)
app.include_router(core_router)
app.include_router(specified_router)
