from fastapi import FastAPI, Depends
from supabase import Client
from schemas.request import ChatRequest
from schemas.response import ChatMessage, ChatResponse, parse_chat_response

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
    get_read_client,
    get_write_client,
)
from agent.state import AgentState, Preferences

app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
async def chat_reply(
    payload: ChatRequest,
    read_db: Client = Depends(get_read_client),
    write_db: Client = Depends(get_write_client),
) -> ChatResponse:
    await upsert_session(write_db, payload.session_id)
    history = await fetch_history(write_db, payload.session_id)
    conversation_summary = await fetch_session_summary(write_db, payload.session_id)
    listings = await fetch_listings(read_db)
    listings_path = write_session_listings(payload.session_id, listings)

    await insert_message(write_db, payload.session_id, "user", payload.query)

    # Build the full message thread: DB history + current user message
    prior_messages = [{"role": m["role"], "content": m["content"]} for m in history]
    prior_messages.append({"role": "user", "content": payload.query})

    # Initialize AgentState
    initial_state = AgentState(
        session_id=payload.session_id,
        messages=prior_messages,
        shortlist=[],
        preferences=Preferences(),
        confidence=0.0,
        verifier_reason=None,
        next_action=None,
        listings_path=listings_path,
        conversation_summary=conversation_summary,
        final_response=None
    )

    result = await graph.ainvoke(initial_state)

    # Convert dictionary to AgentState if necessary or just use result
    final_response = result.get("final_response")
    if not final_response:
        final_response = {"type": "ai_reply", "message": "I am sorry, an error occurred."}

    response = parse_chat_response(final_response)

    if response.type == "ai_reply":
        assistant_content = response.message or ""
        assistant_meta = {}
    else:
        assistant_content = ""
        assistant_meta = {"ids": response.ids} if response.ids else {}

    await insert_message(write_db, payload.session_id, "assistant", assistant_content, assistant_meta)

    new_summary = await update_summary(conversation_summary, payload.query, assistant_content)
    await update_session_summary(write_db, payload.session_id, new_summary)

    return response


@app.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_session_messages(
    session_id: str,
    write_db: Client = Depends(get_write_client),
) -> list[ChatMessage]:
    rows = await fetch_messages(write_db, session_id)
    return [ChatMessage(**row) for row in rows]
