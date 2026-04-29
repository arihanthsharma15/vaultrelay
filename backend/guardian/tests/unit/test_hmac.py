import os

os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

import time

from app.services.hmac import is_message_fresh, sign_message, verify_message


def test_sign_and_verify():
    payload = "test-payload"
    secret = "test-secret"
    signature = sign_message(payload, secret)
    assert verify_message(payload, signature, secret) is True


def test_wrong_secret_fails():
    payload = "test-payload"
    signature = sign_message(payload, "secret-a")
    assert verify_message(payload, signature, "secret-b") is False


def test_tampered_payload_fails():
    secret = "test-secret"
    signature = sign_message("original", secret)
    assert verify_message("tampered", signature, secret) is False


def test_message_fresh():
    now = int(time.time())
    assert is_message_fresh(now) is True


def test_message_stale():
    old = int(time.time()) - 120
    assert is_message_fresh(old) is False
