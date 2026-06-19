import os

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://test:test@localhost/test",
)
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("AUDIT_LOGGING_ENABLED", "false")
