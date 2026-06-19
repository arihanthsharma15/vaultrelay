import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.message import MessageType, TunnelMessage
from app.services.tunnel import manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Temporary hardcoded secret for Phase 1
# Will be fetched from DB per tenant in Phase 2
TENANT_SECRET = "dev-tunnel-secret"


@router.websocket("/ws/{tenant_id}")
async def websocket_tunnel(websocket: WebSocket, tenant_id: str):
    await manager.connect(tenant_id, websocket)
    logger.info(f"[GUARDIAN][WS] tenant={tenant_id} connection established")
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                message = TunnelMessage(**data)

                logger.info(
                    f"[GUARDIAN][WS] <- tenant={tenant_id} type={message.type} "
                    f"request_id={message.request_id}"
                )

                # Verify HMAC signature
                if not message.verify(TENANT_SECRET):
                    logger.warning(
                        f"[GUARDIAN][WS] tenant={tenant_id} INVALID SIGNATURE "
                        f"request_id={message.request_id}"
                    )
                    error = TunnelMessage(
                        type=MessageType.ERROR,
                        tenant_id=tenant_id,
                        payload="Invalid signature",
                    )
                    await websocket.send_text(error.model_dump_json())
                    continue

                # Handle heartbeat
                if message.type == MessageType.HEARTBEAT:
                    ack = TunnelMessage(
                        type=MessageType.HEARTBEAT_ACK,
                        tenant_id=tenant_id,
                        request_id=message.request_id,
                    ).sign(TENANT_SECRET)
                    await websocket.send_text(ack.model_dump_json())
                    logger.info(f"[GUARDIAN][WS] heartbeat ok tenant={tenant_id}")
                    continue

                # Handle query result / error coming back from Sentry.
                # This is the other half of ConnectionManager.send_and_wait():
                # an HTTP handler is blocked on a Future keyed by request_id,
                # waiting for exactly this message to show up.
                if message.type in (MessageType.RESULT, MessageType.ERROR):
                    delivered = manager.resolve(message.request_id, message)
                    if delivered:
                        logger.info(
                            f"[GUARDIAN][WS] resolved pending request "
                            f"request_id={message.request_id} type={message.type}"
                        )
                    else:
                        # Either the HTTP request already timed out and gave
                        # up, or this is a stray/duplicate message. Not fatal,
                        # just log it so it's visible during debugging.
                        logger.warning(
                            f"[GUARDIAN][WS] no pending request for "
                            f"request_id={message.request_id} "
                            f"(tenant={tenant_id}, type={message.type})"
                        )
                    continue

                logger.warning(
                    f"[GUARDIAN][WS] unhandled message type={message.type} "
                    f"from tenant={tenant_id}"
                )

            except Exception as e:
                logger.error(f"[GUARDIAN][WS] message error: {e}")

    except WebSocketDisconnect:
        manager.disconnect(tenant_id)
        logger.info(f"[GUARDIAN][WS] tenant={tenant_id} connection closed")
