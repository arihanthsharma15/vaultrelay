import logging
import time
from typing import Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.routes.nl2sql import router as nl2sql_router
from app.api.ws import router as ws_router
from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.audit_log import AuditLogData
from app.services.audit_logger import log_request
from app.services.rate_limiter import check_rate_limit

logging.basicConfig(level=logging.INFO)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        api_key = request.headers.get("X-API-Key")

        if api_key:
            tenant_id = request.path_params.get("tenant_id", "default")
            api_key_hash = hash(api_key)

            limit = settings.rate_limit_requests_per_minute
            allowed = await check_rate_limit(tenant_id, str(api_key_hash), limit, 60)

            if not allowed:
                return Response("Rate limit exceeded", status_code=429)

        response = await call_next(request)
        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        response = await call_next(request)

        if not settings.audit_logging_enabled:
            return response

        try:
            duration_ms = int((time.time() - start_time) * 1000)

            tenant_id = request.path_params.get("tenant_id", "default")
            api_key_hash = None
            api_key = request.headers.get("X-API-Key")
            if api_key:
                api_key_hash = str(hash(api_key))

            audit_data = AuditLogData(
                tenant_id=tenant_id,
                api_key_id=api_key_hash,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            async for db in get_db():
                await log_request(db, audit_data)
                break
        except Exception:
            pass

        return response


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(AuditLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

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
