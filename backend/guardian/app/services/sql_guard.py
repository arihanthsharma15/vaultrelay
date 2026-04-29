FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
]


def validate_sql(sql: str) -> bool:
    upper_sql = sql.upper()

    if not upper_sql.startswith("SELECT"):
        return False

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in upper_sql:
            return False

    return True
