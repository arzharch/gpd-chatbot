from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict
from openai import AsyncOpenAI
from agent.state import InputState, OutputState
from config import settings
from typing import Dict, Any

from dataclasses import dataclass


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def call_model(state : InputState) -> Dict[str, Any]:

    prompt = (
        "You are a real estate assistant. Ask clarifying questions and reply concisely.\n"
        f"User: {state['user_input']}"
    )

    response = await client.chat.completions.create(
        model = settings.MODEL_NAME,
        messages=[{"role":"user", "content":prompt}]
    )

    message = response.choices[0].message.content or ""

    return {
        "type" : "ai_reply",
        "message" : message,
        "ids" : None
    }

# Define the graph
graph= (StateGraph(InputState, output_schema= OutputState)
        .add_node("call_model", call_model)
        .add_edge("__start__", "call_model")
        .compile(name="GPD Chat")
        )