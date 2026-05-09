from fastapi import FastAPI
from schemas.request import ChatRequest
from schemas.response import ChatResponse

from agent.graph import graph


app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
async def chat_reply(payload : ChatRequest):

    result = await graph.ainvoke({"user_input": payload.query})

    return ChatResponse(**result)