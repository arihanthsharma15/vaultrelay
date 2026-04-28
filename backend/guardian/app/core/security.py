import hashlib
import secrets


def generate_api_key() -> str:
    """Generate a cryptographically secure API key."""
    return f"vr_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA-256 for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify a plain API key against its hash."""
    return hash_api_key(plain_key) == hashed_key
