from fastapi import FastAPI
from schemas.request import ChatRequest
from schemas.response import ChatResponse

from agent.graph import graph
from agent.memory_store import get_memory
from tools.session_listings import write_session_listings
from tools.supabase_client import fetch_listings

app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
async def chat_reply(payload : ChatRequest) -> ChatResponse:
    history = get_memory(payload.session_id)
    listings = await fetch_listings()
    listings_path = write_session_listings(payload.session_id, listings)

    result = await graph.ainvoke(
        {
            "user_input": payload.query,
            "session_id": payload.session_id,
            "history": history,
            "preferences": {},
            "matched_ids": [],
            "listings_path": listings_path,
        }
    )

    return ChatResponse(**result)