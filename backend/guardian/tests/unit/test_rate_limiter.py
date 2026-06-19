from unittest.mock import AsyncMock, patch

import pytest

from app.services.rate_limiter import check_rate_limit


@pytest.mark.asyncio
async def test_rate_limit_allowed_first_request():
    """Test that first request is allowed."""
    with patch("app.services.rate_limiter.get_redis_client") as mock_get_redis:
        mock_client = AsyncMock()
        mock_client.zremrangebyscore = AsyncMock()
        mock_client.zcard = AsyncMock(return_value=0)
        mock_client.zadd = AsyncMock()
        mock_client.expire = AsyncMock()
        mock_get_redis.return_value = mock_client

        result = await check_rate_limit("tenant1", "key_hash", 100, 60)
        assert result is True


@pytest.mark.asyncio
async def test_rate_limit_blocked_when_exceeded():
    """Test that request is blocked when limit exceeded."""
    with patch("app.services.rate_limiter.get_redis_client") as mock_get_redis:
        mock_client = AsyncMock()
        mock_client.zremrangebyscore = AsyncMock()
        mock_client.zcard = AsyncMock(return_value=100)
        mock_get_redis.return_value = mock_client

        result = await check_rate_limit("tenant1", "key_hash", 100, 60)
        assert result is False


@pytest.mark.asyncio
async def test_rate_limit_allows_below_limit():
    """Test that requests are allowed below the limit."""
    with patch("app.services.rate_limiter.get_redis_client") as mock_get_redis:
        mock_client = AsyncMock()
        mock_client.zremrangebyscore = AsyncMock()
        mock_client.zcard = AsyncMock(return_value=50)
        mock_client.zadd = AsyncMock()
        mock_client.expire = AsyncMock()
        mock_get_redis.return_value = mock_client

        result = await check_rate_limit("tenant1", "key_hash", 100, 60)
        assert result is True


@pytest.mark.asyncio
async def test_rate_limit_disabled():
    """Test that rate limiting is disabled when config is false."""
    with patch("app.services.rate_limiter.settings") as mock_settings:
        mock_settings.rate_limit_enabled = False

        result = await check_rate_limit("tenant1", "key_hash", 1, 60)
        assert result is True


@pytest.mark.asyncio
async def test_rate_limit_redis_error_allows_request():
    """Test that Redis errors are gracefully handled (fail open)."""
    with patch("app.services.rate_limiter.get_redis_client") as mock_get_redis:
        mock_get_redis.side_effect = Exception("Redis connection failed")

        result = await check_rate_limit("tenant1", "key_hash", 100, 60)
        assert result is True


@pytest.mark.asyncio
async def test_rate_limit_uses_correct_redis_key():
    """Test that correct Redis key is used for tracking."""
    with patch("app.services.rate_limiter.get_redis_client") as mock_get_redis:
        mock_client = AsyncMock()
        mock_client.zremrangebyscore = AsyncMock()
        mock_client.zcard = AsyncMock(return_value=0)
        mock_client.zadd = AsyncMock()
        mock_client.expire = AsyncMock()
        mock_get_redis.return_value = mock_client

        await check_rate_limit("tenant123", "key_hash_456", 100, 60)

        mock_client.zremrangebyscore.assert_called_once()
        expected_key = "rate_limit:tenant123:key_hash_456"
        call_args = mock_client.zremrangebyscore.call_args
        assert call_args[0][0] == expected_key
