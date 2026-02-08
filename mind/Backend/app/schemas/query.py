from pydantic import BaseModel
from typing import Dict, Any


class QueryRequest(BaseModel):
    query: str
    intent: str


class QueryResponse(BaseModel):
    intent: str
    confidence: float
    responses: Dict[str, Any]
