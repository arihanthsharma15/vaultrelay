from groq import Groq

from app.core.config import get_settings

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
"""


async def generate_sql(question: str) -> str:
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()

    return sql
