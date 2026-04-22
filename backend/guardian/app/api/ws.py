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
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                message = TunnelMessage(**data)

                # Verify HMAC signature
                if not message.verify(TENANT_SECRET):
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
                    logger.info(f"Heartbeat from tenant={tenant_id}")

            except Exception as e:
                logger.error(f"Message error: {e}")

    except WebSocketDisconnect:
        manager.disconnect(tenant_id)
