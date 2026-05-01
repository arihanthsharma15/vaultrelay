from typing import Any


def build_schema_context(schema: list[dict[str, Any]]) -> str:
    """
    Build a schema context string for the LLM.
    Input: list of table dicts with columns
    Output: formatted string describing the schema
    """
    if not schema:
        return "No schema available."

    lines = ["Database Schema:", ""]

    for table in schema:
        table_name = table.get("alias") or table.get("table_name", "unknown")
        lines.append(f"Table: {table_name}")

        columns = table.get("columns", [])
        for col in columns:
            col_name = col.get("alias") or col.get("column_name", "unknown")
            col_type = col.get("column_type", "unknown")
            pii_marker = " [PII]" if col.get("is_pii") else ""
            lines.append(f"  - {col_name} ({col_type}){pii_marker}")

        lines.append("")

    return "\n".join(lines)


def get_sample_schema() -> list[dict[str, Any]]:
    """
    Sample schema for development and testing.
    In production this comes from the database registry.
    """
    return [
        {
            "table_name": "users",
            "alias": "Users",
            "columns": [
                {
                    "column_name": "id",
                    "column_type": "integer",
                    "is_pii": False,
                },
                {
                    "column_name": "name",
                    "column_type": "varchar",
                    "alias": "Full Name",
                    "is_pii": True,
                },
                {
                    "column_name": "email",
                    "column_type": "varchar",
                    "is_pii": True,
                },
                {
                    "column_name": "created_at",
                    "column_type": "timestamp",
                    "is_pii": False,
                },
            ],
        },
        {
            "table_name": "orders",
            "alias": "Orders",
            "columns": [
                {
                    "column_name": "id",
                    "column_type": "integer",
                    "is_pii": False,
                },
                {
                    "column_name": "user_id",
                    "column_type": "integer",
                    "is_pii": False,
                },
                {
                    "column_name": "amount",
                    "column_type": "decimal",
                    "is_pii": False,
                },
                {
                    "column_name": "status",
                    "column_type": "varchar",
                    "is_pii": False,
                },
                {
                    "column_name": "created_at",
                    "column_type": "timestamp",
                    "is_pii": False,
                },
            ],
        },
    ]
