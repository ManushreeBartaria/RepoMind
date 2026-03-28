from fastapi import APIRouter, HTTPException

from ..schemas.query import QueryRequest, QueryResponse, ChatHistoryResponse
from ..core.state import state
from retrieval.main import run

router = APIRouter()


@router.post("/", response_model=QueryResponse)
def query(payload: QueryRequest):
    if state.graph is None:
        raise HTTPException(400, "Ingestion not complete")

    response = run(
        user_query=payload.query,
        frontend_section=payload.intent,
        graph=state.graph
    )

    # Save to chat history
    state.add_to_history(payload.query, payload.intent, response)

    return response


@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history():
    return ChatHistoryResponse(history=state.chat_history)


@router.delete("/history")
def clear_chat_history():
    state.chat_history = []
    state.save_history()
    return {"message": "Chat history cleared"}

    # Save to chat history
    state.add_to_history(payload.query, payload.intent, response)

    return response
