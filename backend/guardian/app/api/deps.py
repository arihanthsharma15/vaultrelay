from fastapi import Header, HTTPException, status

from app.core.security import hash_api_key

VALID_KEY_HASHES: set[str] = set()


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
) -> str:
    """
    Dependency that validates the API key from request header.
    Returns the key hash if valid, raises 401 if not.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    key_hash = hash_api_key(x_api_key)

    if key_hash not in VALID_KEY_HASHES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return key_hash
