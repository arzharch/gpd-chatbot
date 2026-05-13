from typing import Any, Dict
from langgraph.graph import END, StateGraph
from agent.state import AgentState
from agent.guardrails import guardrails_node
from agent.supervisor import supervisor_node
from agent.tool_executor import execute_tools_node
from agent.verifier import verifier_node


def route_after_guardrails(state: AgentState) -> str:
    if state.get("final_response"):
        return END
    return "supervisor"


def route_after_supervisor(state: AgentState) -> str:
    # If supervisor hit an error and set final_response directly, exit.
    if state.get("final_response"):
        return END

    messages = state.get("messages", [])
    if not messages:
        return "wrap_response"

    last_msg = messages[-1]
    if last_msg.get("tool_calls"):
        return "tool_executor"

    # Supervisor returned text without a tool call (shouldn't happen with
    # tool_choice="required", but we handle it gracefully).
    return "wrap_response"


def wrap_response_node(state: AgentState) -> Dict[str, Any]:
    """Safety net: if we reach here, the supervisor produced text without
    calling a tool. Wrap whatever text it returned into a final_response."""
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        content = last_msg.get("content", "").strip()
        if content:
            return {"final_response": {"type": "ai_reply", "message": content}}
    return {
        "final_response": {
            "type": "ai_reply",
            "message": "Could you tell me more about what you're looking for?",
        }
    }


def route_after_tool_executor(state: AgentState) -> str:
    if state.get("final_response"):
        return "verifier"
    return "supervisor"


def route_after_verifier(state: AgentState) -> str:
    if state.get("final_response"):
        return END
    return "supervisor"


graph = (
    StateGraph(AgentState)
    .add_node("guardrails", guardrails_node)
    .add_node("supervisor", supervisor_node)
    .add_node("tool_executor", execute_tools_node)
    .add_node("verifier", verifier_node)
    .add_node("wrap_response", wrap_response_node)
    .add_edge("__start__", "guardrails")
    .add_conditional_edges("guardrails", route_after_guardrails)
    .add_conditional_edges("supervisor", route_after_supervisor)
    .add_conditional_edges("tool_executor", route_after_tool_executor)
    .add_conditional_edges("verifier", route_after_verifier)
    .add_edge("wrap_response", END)
    .compile(name="agent_graph")
)