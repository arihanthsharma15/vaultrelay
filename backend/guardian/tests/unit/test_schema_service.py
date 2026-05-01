import os

os.environ["SECRET_KEY"] = "test-secret"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["GROQ_API_KEY"] = "test-groq-key"

from app.services.schema_service import build_schema_context, get_sample_schema


def test_build_schema_context_empty():
    result = build_schema_context([])
    assert result == "No schema available."


def test_build_schema_context_basic():
    schema = [
        {
            "table_name": "users",
            "columns": [
                {"column_name": "id", "column_type": "integer", "is_pii": False},
                {"column_name": "email", "column_type": "varchar", "is_pii": True},
            ],
        }
    ]
    result = build_schema_context(schema)
    assert "users" in result
    assert "id" in result
    assert "email" in result
    assert "[PII]" in result


def test_build_schema_context_uses_alias():
    schema = [
        {
            "table_name": "usr_tbl",
            "alias": "Users",
            "columns": [
                {
                    "column_name": "usr_nm",
                    "alias": "Username",
                    "column_type": "varchar",
                    "is_pii": False,
                },
            ],
        }
    ]
    result = build_schema_context(schema)
    assert "Users" in result
    assert "Username" in result
    assert "usr_tbl" not in result
    assert "usr_nm" not in result


def test_get_sample_schema_structure():
    schema = get_sample_schema()
    assert len(schema) > 0
    for table in schema:
        assert "table_name" in table
        assert "columns" in table
        for col in table["columns"]:
            assert "column_name" in col
            assert "column_type" in col
            assert "is_pii" in col


def test_pii_columns_marked():
    schema = get_sample_schema()
    context = build_schema_context(schema)
    assert "[PII]" in context
