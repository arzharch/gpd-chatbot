from typing import Any, Dict
from guardrails.checks import run_all_checks
from agent.state import AgentState

def guardrails_node(state: AgentState) -> Dict[str, Any]:
    last_msg = state["messages"][-1]
    if last_msg["role"] != "user":
        return {}
        
    ok, message = run_all_checks(last_msg["content"])
    if not ok:
        return {
            "final_response": {
                "type": "ai_reply",
                "message": message,
                "ids": []
            }
        }
    return {}
