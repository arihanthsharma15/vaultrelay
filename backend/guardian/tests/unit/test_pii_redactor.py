import os

os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["GROQ_API_KEY"] = "test-groq-key"

from app.services.pii_redactor import redact_results, redact_value


def test_redact_email():
    value, count = redact_value("Contact john.doe@example.com for info")
    assert "[REDACTED EMAIL]" in value
    assert count == 1


def test_redact_phone():
    value, count = redact_value("Call us at 987-654-3210")
    assert "[REDACTED PHONE]" in value
    assert count == 1


def test_redact_credit_card():
    value, count = redact_value("Card: 4111 1111 1111 1111")
    assert "[REDACTED CARD]" in value
    assert count == 1


def test_redact_ip():
    value, count = redact_value("IP: 192.168.1.1")
    assert "[REDACTED IP]" in value
    assert count == 1


def test_no_pii_unchanged():
    value, count = redact_value("Total orders: 42")
    assert value == "Total orders: 42"
    assert count == 0


def test_redact_results_pattern_based():
    results = {
        "columns": ["id", "email", "name"],
        "rows": [
            [1, "john@example.com", "John"],
            [2, "jane@example.com", "Jane"],
        ],
        "row_count": 2,
    }
    redacted, count = redact_results(results)
    assert count == 2
    for row in redacted["rows"]:
        assert "[REDACTED EMAIL]" in row[1]


def test_redact_results_column_suppression():
    results = {
        "columns": ["id", "email", "name"],
        "rows": [
            [1, "john@example.com", "John Doe"],
        ],
        "row_count": 1,
    }
    redacted, count = redact_results(results, pii_columns=["email", "name"])
    assert redacted["rows"][0][1] == "[REDACTED]"
    assert redacted["rows"][0][2] == "[REDACTED]"


def test_redact_empty_results():
    redacted, count = redact_results({})
    assert count == 0


def test_non_string_values_unchanged():
    results = {
        "columns": ["id", "amount"],
        "rows": [[1, 9999.99]],
        "row_count": 1,
    }
    redacted, count = redact_results(results)
    assert redacted["rows"][0][1] == 9999.99
    assert count == 0
