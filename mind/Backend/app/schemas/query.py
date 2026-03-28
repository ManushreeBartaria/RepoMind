from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime


class QueryRequest(BaseModel):
    query: str
    intent: str


class QueryResponse(BaseModel):
    intent: str
    confidence: float
    responses: Dict[str, Any]


class ChatHistoryEntry(BaseModel):
    timestamp: str
    query: str
    intent: str
    response: Dict[str, Any]


class ChatHistoryResponse(BaseModel):
    history: List[ChatHistoryEntry]
