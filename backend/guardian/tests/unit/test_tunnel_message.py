import os

os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

from app.models.message import MessageType, TunnelMessage


def test_message_sign_and_verify():
    msg = TunnelMessage(
        type=MessageType.HEARTBEAT,
        tenant_id="tenant-123",
    ).sign("test-secret")
    assert msg.hmac != ""
    assert msg.verify("test-secret") is True


def test_message_wrong_secret_fails():
    msg = TunnelMessage(
        type=MessageType.HEARTBEAT,
        tenant_id="tenant-123",
    ).sign("secret-a")
    assert msg.verify("secret-b") is False


def test_message_has_request_id():
    msg = TunnelMessage(
        type=MessageType.QUERY,
        tenant_id="tenant-123",
        payload="SELECT 1",
    )
    assert msg.request_id != ""


def test_message_types():
    assert MessageType.HEARTBEAT == "heartbeat"
    assert MessageType.QUERY == "query"
    assert MessageType.RESULT == "result"
