import hashlib
import hmac
import time


def sign_message(payload: str, secret: str) -> str:
    """Sign a message payload using HMAC-SHA256."""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_message(payload: str, signature: str, secret: str) -> bool:
    """Verify a message signature."""
    expected = sign_message(payload, secret)
    return hmac.compare_digest(expected, signature)


def is_message_fresh(timestamp: int, max_age_seconds: int = 60) -> bool:
    """Check if a message timestamp is within acceptable window."""
    now = int(time.time())
    return abs(now - timestamp) <= max_age_seconds
