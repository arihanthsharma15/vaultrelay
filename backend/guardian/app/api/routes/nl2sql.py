import json
import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.message import MessageType, TunnelMessage
from app.schemas.audit_log import AuditLogData
from app.schemas.nl2sql import NLQueryRequest, NLQueryResponse
from app.services.audit_logger import log_request
from app.services.groq_service import generate_sql
from app.services.pii_redactor import redact_results
from app.services.sql_guard import validate_sql
from app.services.tunnel import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/query", tags=["nl2sql"])

# Same temporary shared secret used in ws.py for Phase 1.
# Both sides must agree on this until per-tenant secrets land (Phase 2).
TENANT_SECRET = "dev-tunnel-secret"

QUERY_TIMEOUT_SECONDS = 35.0


@router.post("/{tenant_id}", response_model=NLQueryResponse)
async def natural_language_query(
    tenant_id: str,
    payload: NLQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    t_start = time.monotonic()
    logger.info(f"[GUARDIAN][QUERY] tenant={tenant_id} question={payload.question!r}")

    # 1. NL -> SQL
    t0 = time.monotonic()
    sql = await generate_sql(payload.question)

    logger.info(
        "[GUARDIAN][QUERY] tenant=%s groq_sql=%r groq_ms=%s",
        tenant_id,
        sql,
        int((time.monotonic() - t0) * 1000),
    )

    if not validate_sql(sql):
        logger.warning(
            "[GUARDIAN][QUERY] tenant=%s REJECTED by sql_guard: %r",
            tenant_id,
            sql,
        )
        raise HTTPException(
            status_code=400,
            detail="Generated SQL failed validation",
        )

    # 2. Make sure there's actually a Sentry to send this to before we
    #    bother building/signing a message.
    if not manager.is_connected(tenant_id):
        logger.warning(f"[GUARDIAN][QUERY] tenant={tenant_id} NO SENTRY CONNECTED")
        raise HTTPException(
            status_code=503,
            detail=f"No Sentry agent connected for tenant '{tenant_id}'",
        )

    # 3. Dispatch over the tunnel and block until Sentry replies (or times out)
    query_msg = TunnelMessage(
        type=MessageType.QUERY,
        tenant_id=tenant_id,
        payload=sql,
    ).sign(TENANT_SECRET)

    logger.info(
        f"[GUARDIAN][QUERY] -> dispatching to sentry "
        f"tenant={tenant_id} request_id={query_msg.request_id}"
    )

    t1 = time.monotonic()
    try:
        response_msg: TunnelMessage = await manager.send_and_wait(
            tenant_id, query_msg, timeout=QUERY_TIMEOUT_SECONDS
        )
    except TimeoutError as e:
        logger.error(f"[GUARDIAN][QUERY] tenant={tenant_id} TIMEOUT: {e}")
        raise HTTPException(status_code=504, detail=str(e))
    except ConnectionError as e:
        logger.error(f"[GUARDIAN][QUERY] tenant={tenant_id} CONNECTION ERROR: {e}")
        raise HTTPException(status_code=503, detail=str(e))

    tunnel_ms = int((time.monotonic() - t1) * 1000)
    logger.info(
        f"[GUARDIAN][QUERY] <- sentry replied tenant={tenant_id} "
        f"request_id={response_msg.request_id} type={response_msg.type} "
        f"tunnel_ms={tunnel_ms}"
    )

    if response_msg.type == MessageType.ERROR:
        logger.warning(
            "[GUARDIAN][QUERY] tenant=%s sentry rejected: %s",
            tenant_id,
            response_msg.payload,
        )
        raise HTTPException(
            status_code=400,
            detail=f"Sentry rejected query: {response_msg.payload}",
        )

    # 4. Sentry's payload is a JSON string:
    # {"columns": [...], "rows": [...], "row_count": N}
    try:
        raw_results = json.loads(response_msg.payload)
    except json.JSONDecodeError:
        logger.error(
            "[GUARDIAN][QUERY] tenant=%s unparseable payload from sentry",
            tenant_id,
        )       
        raise HTTPException(
            status_code=502,
            detail="Sentry returned an unparseable result payload",
        )

    # 5. Redact PII before this ever leaves Guardian.
    #    pii_columns=None for now — column-level suppression needs the
    #    schema metadata registry (PRD 8.4) which isn't built yet, so we
    #    rely on pattern-based redaction only at this stage.
    redacted_results, redaction_count = redact_results(raw_results, pii_columns=None)
    logger.info(
        "[GUARDIAN][QUERY] tenant=%s rows=%s redactions=%s",
        tenant_id,
        redacted_results.get("row_count", 0),
        redaction_count,
    )

    # 6. Audit log. Fire-and-forget semantics are already handled inside
    #    log_request (it swallows its own errors), so a logging failure
    #    here never breaks the user-facing response.
    audit_data = AuditLogData(
        tenant_id=tenant_id,
        api_key_id=None,
        endpoint=f"/v1/query/{tenant_id}",
        method="POST",
        status_code=200,
        request_body=json.dumps({"question": payload.question, "sql": sql}),
        response_summary=(
            f"rows={redacted_results.get('row_count', 0)} "
            f"redactions={redaction_count}"
        ),
        duration_ms=int((time.monotonic() - t_start) * 1000),
        ip_address=None,
        user_agent=None,
    )
    await log_request(db, audit_data)

    total_ms = int((time.monotonic() - t_start) * 1000)
    logger.info(f"[GUARDIAN][QUERY] tenant={tenant_id} COMPLETE total_ms={total_ms}")

    return NLQueryResponse(sql=sql, results=redacted_results)
