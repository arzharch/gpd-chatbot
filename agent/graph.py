from typing import Any, Dict

from langgraph.graph import StateGraph
from openai import AsyncOpenAI

from agent.state import InputState, OutputState
from agent.memory_store import save_memory
from config import settings


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def call_model(state: InputState) -> Dict[str, Any]:
    history = state["history"]
    session_id = state["session_id"]

    messages = history + [{"role": "user", "content": state["user_input"]}]

    response = await client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=messages,
    )

    message = response.choices[0].message.content or ""

    messages.append({"role": "assistant", "content": message})
    save_memory(session_id, messages)

    return {
        "type": "ai_reply",
        "message": message,
        "ids": None,
    }

# Define the graph
graph= (StateGraph(InputState, output_schema= OutputState)
        .add_node("call_model", call_model)
        .add_edge("__start__", "call_model")
        .compile(name="GPD Chat")
        )