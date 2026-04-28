import time
import uuid
from enum import Enum

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    QUERY = "query"
    RESULT = "result"
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"
    AUTH = "auth"
    AUTH_ACK = "auth_ack"
    ERROR = "error"


class TunnelMessage(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    tenant_id: str
    payload: str = ""
    hmac: str = ""
    timestamp: int = Field(default_factory=lambda: int(time.time()))

    def _signing_payload(self) -> str:
        return (
            f"{self.request_id}:{self.type}:"
            f"{self.tenant_id}:{self.payload}:{self.timestamp}"
        )

    def sign(self, secret: str) -> "TunnelMessage":
        from app.services.hmac import sign_message
        self.hmac = sign_message(self._signing_payload(), secret)
        return self

    def verify(self, secret: str) -> bool:
        from app.services.hmac import is_message_fresh, verify_message
        if not is_message_fresh(self.timestamp):
            return False
        return verify_message(self._signing_payload(), self.hmac, secret)
