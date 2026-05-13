import json
import logging
from typing import Any, Dict

from tools import TOOLS
from agent.state import AgentState

logger = logging.getLogger(__name__)

tools_by_name = {t.name: t for t in TOOLS}


def execute_tools_node(state: AgentState) -> Dict[str, Any]:
    messages = state["messages"]
    last_msg = messages[-1]

    if not last_msg.get("tool_calls"):
        return {}

    new_messages: list[dict] = []
    shortlist = list(state.get("shortlist", []))
    final_response = state.get("final_response")

    for tc in last_msg["tool_calls"]:
        tool_name = tc["function"]["name"]

        try:
            tool_args = json.loads(tc["function"]["arguments"])
        except json.JSONDecodeError as e:
            logger.warning("Bad tool arguments from LLM for %s: %s", tool_name, e)
            new_messages.append({
                "role": "tool",
                "content": f"Error: could not parse arguments — {e}",
                "tool_call_id": tc["id"],
                "name": tool_name,
            })
            continue

        if tool_name not in tools_by_name:
            logger.warning("LLM called unknown tool: %s", tool_name)
            new_messages.append({
                "role": "tool",
                "content": f"Error: unknown tool '{tool_name}'",
                "tool_call_id": tc["id"],
                "name": tool_name,
            })
            continue

        tool = tools_by_name[tool_name]
        try:
            result = tool.invoke(tool_args)
            new_messages.append({
                "role": "tool",
                "content": str(result),
                "tool_call_id": tc["id"],
                "name": tool_name,
            })

            # ── Side effects ──
            if tool_name == "add_to_shortlist":
                parsed = json.loads(result)
                shortlist = list(set(shortlist + parsed.get("ids", [])))

            elif tool_name == "remove_from_shortlist":
                parsed = json.loads(result)
                for rid in parsed.get("ids", []):
                    if rid in shortlist:
                        shortlist.remove(rid)

            elif tool_name == "finalise_recommendation":
                parsed = json.loads(result)
                final_response = {
                    "type": "ids",
                    "ids": parsed.get("ids", []),
                }

            elif tool_name == "ask_clarification":
                final_response = {
                    "type": "ai_reply",
                    "message": tool_args.get("message", "Could you please clarify?"),
                }

        except Exception as e:
            logger.exception("Tool %s execution failed", tool_name)
            new_messages.append({
                "role": "tool",
                "content": f"Error executing tool: {str(e)}",
                "tool_call_id": tc["id"],
                "name": tool_name,
            })

    return {
        "messages": new_messages,
        "shortlist": shortlist,
        "final_response": final_response,
    }
