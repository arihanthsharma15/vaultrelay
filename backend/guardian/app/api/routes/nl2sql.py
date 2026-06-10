from fastapi import APIRouter, HTTPException

from app.schemas.nl2sql import (
    NLQueryRequest,
    NLQueryResponse,
)
from app.services.groq_service import generate_sql
from app.services.sql_guard import validate_sql

router = APIRouter(prefix="/v1/query", tags=["nl2sql"])


@router.post("", response_model=NLQueryResponse)
async def natural_language_query(payload: NLQueryRequest):
    sql = await generate_sql(payload.question)

    if not validate_sql(sql):
        raise HTTPException(
            status_code=400,
            detail="Generated SQL failed validation",
        )

    return NLQueryResponse(sql=sql)
