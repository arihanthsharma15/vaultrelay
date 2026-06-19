from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.message import MessageType, TunnelMessage

client = TestClient(app)


@patch("app.api.routes.nl2sql.manager.send_and_wait")
@patch("app.api.routes.nl2sql.manager.is_connected")
@patch("app.services.groq_service.client")
def test_nl2sql_endpoint(
    mock_groq_client,
    mock_is_connected,
    mock_send_and_wait,
):
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="SELECT * FROM users LIMIT 100"
            )
        )
    ]
    mock_groq_client.chat.completions.create.return_value = mock_response

    mock_is_connected.return_value = True

    mock_send_and_wait.return_value = TunnelMessage(
        type=MessageType.RESULT,
        tenant_id="development",
        payload='{"columns":["id"],"rows":[[1]],"row_count":1}',
    )

    response = client.post(
        "/v1/query/development",
        json={"question": "show all users"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sql"] == "SELECT * FROM users LIMIT 100"
    assert data["results"]["row_count"] == 1