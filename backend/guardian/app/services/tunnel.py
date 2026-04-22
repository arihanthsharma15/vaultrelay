import logging
from typing import Dict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, tenant_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[tenant_id] = websocket
        logger.info(f"Sentry connected: tenant={tenant_id}")

    def disconnect(self, tenant_id: str):
        if tenant_id in self.active_connections:
            del self.active_connections[tenant_id]
            logger.info(f"Sentry disconnected: tenant={tenant_id}")

    async def send(self, tenant_id: str, message: str):
        ws = self.active_connections.get(tenant_id)
        if ws:
            await ws.send_text(message)

    def is_connected(self, tenant_id: str) -> bool:
        return tenant_id in self.active_connections


manager = ConnectionManager()
