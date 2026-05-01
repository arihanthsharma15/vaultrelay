import re
from typing import Any


# Default PII patterns
PII_PATTERNS = {
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    ),
    "phone": re.compile(
        r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    ),
    "ssn": re.compile(
        r"\b\d{3}-\d{2}-\d{4}\b"
    ),
    "credit_card": re.compile(
        r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
    ),
    "ip_address": re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ),
    "pan_card": re.compile(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
    ),
    "aadhaar": re.compile(
        r"\b\d{4}\s?\d{4}\s?\d{4}\b"
    ),
}

REDACTION_LABEL = {
    "email": "[REDACTED EMAIL]",
    "phone": "[REDACTED PHONE]",
    "ssn": "[REDACTED SSN]",
    "credit_card": "[REDACTED CARD]",
    "ip_address": "[REDACTED IP]",
    "pan_card": "[REDACTED PAN]",
    "aadhaar": "[REDACTED AADHAAR]",
}


def redact_value(value: str) -> tuple[str, int]:
    """
    Redact PII from a string value.
    Returns (redacted_value, count_of_redactions)
    """
    redacted = value
    count = 0

    for pii_type, pattern in PII_PATTERNS.items():
        label = REDACTION_LABEL[pii_type]
        new_value, n = pattern.subn(label, redacted)
        if n > 0:
            redacted = new_value
            count += n

    return redacted, count


def redact_results(
    results: dict[str, Any],
    pii_columns: list[str] | None = None,
) -> tuple[dict[str, Any], int]:
    """
    Redact PII from query results.
    - Pattern based redaction on all string values
    - Column level suppression for known PII columns
    Returns (redacted_results, total_redaction_count)
    """
    if not results:
        return results, 0

    columns = results.get("columns", [])
    rows = results.get("rows", [])
    total_redactions = 0

    # Find PII column indices
    pii_indices = set()
    if pii_columns:
        for i, col in enumerate(columns):
            if col.lower() in [p.lower() for p in pii_columns]:
                pii_indices.add(i)

    redacted_rows = []
    for row in rows:
        redacted_row = []
        for i, cell in enumerate(row):
            if i in pii_indices:
                redacted_row.append("[REDACTED]")
                total_redactions += 1
            elif isinstance(cell, str):
                redacted_cell, count = redact_value(cell)
                redacted_row.append(redacted_cell)
                total_redactions += count
            else:
                redacted_row.append(cell)
        redacted_rows.append(redacted_row)

    return {
        "columns": columns,
        "rows": redacted_rows,
        "row_count": results.get("row_count", len(redacted_rows)),
    }, total_redactions
