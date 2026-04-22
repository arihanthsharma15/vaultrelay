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

    def sign(self, secret: str) -> "TunnelMessage":
        from app.services.hmac import sign_message
        signing_payload = f"{self.request_id}:{self.type}:{self.tenant_id}:{self.payload}:{self.timestamp}"
        self.hmac = sign_message(signing_payload, secret)
        return self

    def verify(self, secret: str) -> bool:
        from app.services.hmac import verify_message, is_message_fresh
        if not is_message_fresh(self.timestamp):
            return False
        signing_payload = f"{self.request_id}:{self.type}:{self.tenant_id}:{self.payload}:{self.timestamp}"
        return verify_message(signing_payload, self.hmac, secret)
