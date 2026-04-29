from pydantic import BaseModel


class NLQueryRequest(BaseModel):
    question: str


class NLQueryResponse(BaseModel):
    sql: str
