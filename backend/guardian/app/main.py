import logging

from fastapi import FastAPI

from app.api.routes.nl2sql import router as nl2sql_router
from app.api.ws import router as ws_router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

# Existing websocket routes
app.include_router(ws_router)

# New NL-to-SQL routes
app.include_router(nl2sql_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "guardian",
        "env": settings.app_env,
    }