from fastapi import FastAPI
from schemas.request import ChatRequest
from schemas.response import ChatMessage, ChatResponse

from agent.graph import graph
from tools.session_listings import write_session_listings
from agent.summarizer import update_summary
from tools.supabase_client import (
    fetch_history,
    fetch_listings,
    fetch_messages,
    fetch_session_summary,
    insert_message,
    update_session_summary,
    upsert_session,
)

app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
async def chat_reply(payload : ChatRequest) -> ChatResponse:
    await upsert_session(payload.session_id)
    history = await fetch_history(payload.session_id)
    conversation_summary = await fetch_session_summary(payload.session_id)
    listings = await fetch_listings()
    listings_path = write_session_listings(payload.session_id, listings)

    await insert_message(payload.session_id, "user", payload.query)

    result = await graph.ainvoke(
        {
            "user_input": payload.query,
            "session_id": payload.session_id,
            "history": history,
            "conversation_summary": conversation_summary,
            "preferences": {},
            "matched_ids": [],
            "listings_path": listings_path,
            "guardrails_blocked": False,
            "verifier_score": None,
            "verifier_retries": 0,
            "response_context": {},
            "message": None,
            "ids": None,
        }
    )

    response = ChatResponse(**result)
    assistant_content = response.message or ""
    assistant_meta = {"ids": response.ids} if response.ids else {}
    await insert_message(payload.session_id, "assistant", assistant_content, assistant_meta)

    new_summary = await update_summary(conversation_summary, payload.query, assistant_content)
    await update_session_summary(payload.session_id, new_summary)

    return response


@app.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_session_messages(session_id: str) -> list[ChatMessage]:
    rows = await fetch_messages(session_id)
    return [ChatMessage(**row) for row in rows]