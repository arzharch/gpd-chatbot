import json
import logging
from typing import Any, Dict

from openai import AsyncOpenAI

from config import settings
from tools import TOOLS
from agent.state import AgentState

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Build clean OpenAI tool schemas from our Langchain tools.
# We strip Pydantic v2 artifacts ($defs, title) that confuse the API.
def _build_openai_tools() -> list[dict]:
    result = []
    for t in TOOLS:
        raw = t.args_schema.model_json_schema()
        # Remove keys OpenAI does not expect at the top level of parameters
        params = {k: v for k, v in raw.items() if k not in ("title", "$defs")}
        result.append({
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": params,
            },
        })
    return result

openai_tools = _build_openai_tools()

SUPERVISOR_SYSTEM_PROMPT = """You are an intelligent real estate concierge supervisor.
Your job is to read the user's message and the conversation history, and decide the next best action.

IMPORTANT: You MUST always respond by calling exactly one tool. Never reply with plain text.

Available tools:
- query_properties: search for properties based on filters (type, location, beds, club_id, furnished). Requires listings_path.
- ask_clarification: ask the user a question, greet them, or reply to chitchat. Use this for ANY text response.
- add_to_shortlist: add property IDs to the user's shortlist.
- remove_from_shortlist: remove property IDs from the shortlist.
- compare_properties: compare shortlisted properties side by side. Requires listings_path.
- finalise_recommendation: provide the final recommendation with property IDs and a message.

Decision flow:
1. Greeting or off-topic → ask_clarification with a friendly redirect.
2. Property search with missing info (need at least property type OR budget) → ask_clarification.
3. Property search with enough info → query_properties.
4. After query results, ready to recommend → finalise_recommendation.
5. User wants to compare → compare_properties.

Budget mapping: "under 5 cr" → club_id="under-5cr", "under 15 cr" → club_id="under-15cr", "under 25 cr" → club_id="under-25cr".
Property types: APARTMENT, VILLA, LAND.
"""

async def supervisor_node(state: AgentState) -> Dict[str, Any]:
    messages = state["messages"]

    # Construct OpenAI messages
    summary = state.get("conversation_summary") or ""
    system_content = (
        SUPERVISOR_SYSTEM_PROMPT
        + f"\n\nlistings_path: {state['listings_path']}"
        + f"\nVerifier feedback: {state.get('verifier_reason') or 'none'}"
    )
    if summary:
        system_content += f"\n\nConversation summary (older context):\n{summary}"
    oai_messages: list[dict] = [{"role": "system", "content": system_content}]

    for msg in messages:
        if msg.get("tool_calls"):
            oai_messages.append({
                "role": "assistant",
                "content": msg.get("content") or "",
                "tool_calls": msg["tool_calls"],
            })
        elif msg.get("tool_call_id"):
            oai_messages.append({
                "role": "tool",
                "content": msg.get("content") or "",
                "tool_call_id": msg["tool_call_id"],
            })
        else:
            oai_messages.append({
                "role": msg["role"],
                "content": msg.get("content") or "",
            })

    try:
        response = await client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=oai_messages,
            tools=openai_tools,
            tool_choice="required",
        )

        choice = response.choices[0]
        message = choice.message

        new_msg: Dict[str, Any] = {
            "role": "assistant",
            "content": message.content or "",
        }
        if message.tool_calls:
            new_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]

        return {"messages": [new_msg]}

    except Exception as e:
        logger.exception("Supervisor LLM call failed")
        # Return a safe fallback that sets final_response directly
        # so the graph can exit cleanly.
        return {
            "final_response": {
                "type": "ai_reply",
                "message": "I'm sorry, I ran into a temporary issue. Please try again.",
            }
        }
