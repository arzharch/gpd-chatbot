from fastapi import FastAPI
from schemas.request import ChatRequest
from schemas.response import ChatResponse

from agent.graph import graph
from agent.memory_store import get_memory

from agent.graph import graph


app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
async def chat_reply(payload : ChatRequest) -> ChatResponse:

    history=get_memory(payload.session_id)

    result = await graph.ainvoke(
        {"user_input": payload.query,
         "session_id" : payload.session_id,
         "history": history
         }
    )

    return ChatResponse(**result)