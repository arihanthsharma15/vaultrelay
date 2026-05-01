import os

os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["GROQ_API_KEY"] = "test-groq-key"

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.services.groq_service.client")
def test_nl2sql_endpoint(mock_groq_client):
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content="SELECT * FROM users LIMIT 100")
        )
    ]
    mock_groq_client.chat.completions.create.return_value = mock_response

    response = client.post(
        "/v1/query",
        json={"question": "show all users"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sql"] == "SELECT * FROM users LIMIT 100"
