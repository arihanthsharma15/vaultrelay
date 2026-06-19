import asyncio
import logging
from typing import Dict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Tracks live Sentry WebSocket connections and bridges HTTP request/response
    flow across the async tunnel.

    Pattern: each outbound query gets an asyncio.Future stored under its
    request_id. The HTTP handler awaits that Future. When the WebSocket
    read-loop later sees a `result` or `error` message carrying the same
    request_id, it resolves the Future, which wakes the waiting HTTP handler.

    NOTE: this is in-memory and per-process. It only works for a single
    Guardian instance. If Guardian is ever horizontally scaled, this needs
    to move to something shared (e.g. Redis pub/sub) since a result could
    arrive on a different process than the one holding the Future.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pending: Dict[str, asyncio.Future] = {}
        # request_id -> tenant_id, so disconnect() can fail the right futures
        self._pending_tenant: Dict[str, str] = {}

    async def connect(self, tenant_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[tenant_id] = websocket
        logger.info(f"Sentry connected: tenant={tenant_id}")

    def disconnect(self, tenant_id: str):
        if tenant_id in self.active_connections:
            del self.active_connections[tenant_id]
            logger.info(f"Sentry disconnected: tenant={tenant_id}")

        # Fail any requests still waiting on this tenant's connection —
        # otherwise they'd hang uselessly until their own timeout fires.
        stale_request_ids = [
            rid for rid, tid in self._pending_tenant.items() if tid == tenant_id
        ]
        for rid in stale_request_ids:
            fut = self.pending.pop(rid, None)
            self._pending_tenant.pop(rid, None)
            if fut and not fut.done():
                fut.set_exception(
                    ConnectionError(
                        f"Sentry disconnected mid-query "
                        f"(tenant={tenant_id})"
                    )                   
                        )

    def is_connected(self, tenant_id: str) -> bool:
        return tenant_id in self.active_connections

    async def send(self, tenant_id: str, message: str):
        ws = self.active_connections.get(tenant_id)
        if ws:
            await ws.send_text(message)

    def resolve(self, request_id: str, result) -> bool:
        """
        Called from the WebSocket read-loop when a `result` or `error`
        message arrives. Resolves the matching Future if one is waiting.
        Returns True if something was waiting, False otherwise (e.g. the
        HTTP request already timed out and gave up).
        """
        fut = self.pending.pop(request_id, None)
        self._pending_tenant.pop(request_id, None)
        if fut is None or fut.done():
            return False
        fut.set_result(result)
        return True

    async def send_and_wait(
        self,
        tenant_id: str,
        message,  # TunnelMessage, already signed
        timeout: float = 35.0,
    ):
        """
        Sends a TunnelMessage to the given tenant's Sentry connection and
        blocks until a matching result/error comes back, or until timeout.

        Raises:
            ConnectionError: no Sentry connected for this tenant
            TimeoutError: no response within `timeout` seconds
        """
        if not self.is_connected(tenant_id):
            raise ConnectionError(f"No Sentry connected for tenant={tenant_id}")

        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        self.pending[message.request_id] = fut
        self._pending_tenant[message.request_id] = tenant_id

        try:
            await self.send(tenant_id, message.model_dump_json())
            return await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Sentry did not respond within {timeout}s "
                f"(request_id={message.request_id})"
            )
        finally:
            # Clean up if still pending (e.g. timeout fired) so we don't leak.
            self.pending.pop(message.request_id, None)
            self._pending_tenant.pop(message.request_id, None)


manager = ConnectionManager()
