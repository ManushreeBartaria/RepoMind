from fastapi import APIRouter, HTTPException

from app.schemas.query import QueryRequest, QueryResponse
from app.core.state import state
from retrieval.main import run

router = APIRouter()


@router.post("/", response_model=QueryResponse)
def query(payload: QueryRequest):
    if state.graph is None:
        raise HTTPException(400, "Ingestion not complete")

    return run(
        user_query=payload.query,
        frontend_section=payload.intent,
        graph=state.graph
    )
