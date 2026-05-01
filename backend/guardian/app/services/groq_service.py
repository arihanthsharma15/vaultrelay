from groq import Groq

from app.core.config import get_settings
from app.services.schema_service import build_schema_context, get_sample_schema

settings = get_settings()

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """
You are a PostgreSQL SQL generator.

RULES:
1. ONLY generate SELECT queries
2. NEVER generate INSERT/UPDATE/DELETE/DROP/ALTER
3. NEVER explain anything
4. NEVER use markdown
5. Return ONLY raw SQL
6. LIMIT all queries to 100 rows
7. Use ONLY the tables and columns provided in the schema
"""


async def generate_sql(question: str) -> str:
    schema = get_sample_schema()
    schema_context = build_schema_context(schema)

    prompt = f"{schema_context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()

    return sql
