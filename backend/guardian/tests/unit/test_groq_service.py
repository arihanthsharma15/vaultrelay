import os

os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["GROQ_API_KEY"] = "test-groq-key"

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.groq_service import generate_sql


@pytest.mark.asyncio
@patch("app.services.groq_service.client")
async def test_generate_sql(mock_client):
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content="SELECT * FROM users LIMIT 100")
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response

    sql = await generate_sql("show all users")
    assert sql == "SELECT * FROM users LIMIT 100"
