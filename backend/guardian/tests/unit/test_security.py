import os
os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

from app.core.security import generate_api_key, hash_api_key, verify_api_key


def test_generate_api_key_format():
    key = generate_api_key()
    assert key.startswith("vr_")
    assert len(key) > 10


def test_generate_api_key_unique():
    key1 = generate_api_key()
    key2 = generate_api_key()
    assert key1 != key2


def test_hash_api_key():
    key = "vr_testkey123"
    hashed = hash_api_key(key)
    assert hashed != key
    assert len(hashed) == 64


def test_verify_api_key_correct():
    key = generate_api_key()
    hashed = hash_api_key(key)
    assert verify_api_key(key, hashed) is True


def test_verify_api_key_wrong():
    key = generate_api_key()
    hashed = hash_api_key(key)
    assert verify_api_key("vr_wrongkey", hashed) is False


def test_hash_is_deterministic():
    key = "vr_testkey123"
    assert hash_api_key(key) == hash_api_key(key)
