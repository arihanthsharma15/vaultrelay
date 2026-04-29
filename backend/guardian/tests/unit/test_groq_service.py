from unittest.mock import MagicMock, patch

import pytest

from app.services.groq_service import generate_sql


@pytest.mark.asyncio
@patch("app.services.groq_service.get_groq_client")
async def test_generate_sql(mock_client_factory):
    mock_client = MagicMock()

    mock_response = MagicMock()

    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="SELECT * FROM users LIMIT 100"
            )
        )
    ]

    mock_client.chat.completions.create.return_value = mock_response

    mock_client_factory.return_value = mock_client

    sql = await generate_sql("show all users")

    assert sql == "SELECT * FROM users LIMIT 100"
