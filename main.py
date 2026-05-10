from fastapi import FastAPI
from schemas.request import ChatRequest
from schemas.response import ChatMessage, ChatResponse

from agent.graph import graph
from agent.memory_store import get_memory
from tools.session_listings import write_session_listings
from tools.supabase_client import fetch_listings, fetch_messages, insert_message, upsert_session

app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
async def chat_reply(payload : ChatRequest) -> ChatResponse:
    history = get_memory(payload.session_id)
    listings = await fetch_listings()
    listings_path = write_session_listings(payload.session_id, listings)

    await upsert_session(payload.session_id)
    await insert_message(payload.session_id, "user", payload.query)

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

    response = ChatResponse(**result)
    assistant_content = response.message or ""
    assistant_meta = {"ids": response.ids} if response.ids else {}
    await insert_message(payload.session_id, "assistant", assistant_content, assistant_meta)

    return response


@app.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_session_messages(session_id: str) -> list[ChatMessage]:
    rows = await fetch_messages(session_id)
    return [ChatMessage(**row) for row in rows]