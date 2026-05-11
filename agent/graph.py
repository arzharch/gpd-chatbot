from typing import Any, Dict

from langgraph.graph import END, StateGraph

from agent.guardrails import guardrails_node
from agent.response_writer import compose_response
from agent.state import InputState, OutputState
from agent.supervisor import should_retry
from agent.verifier import verify_response
from config import settings
from tools.collect_preferences import collect_preferences
from tools.compare import filter_properties
from tools.finalise import finalise


async def run_preferences(state: InputState) -> Dict[str, Any]:
    prefs = await collect_preferences(
        state["user_input"],
        state.get("conversation_summary"),
        state.get("history"),
    )
    return {"preferences": prefs}


def run_filter(state: InputState) -> Dict[str, Any]:
    ids = filter_properties(state["preferences"], state["listings_path"])
    return {"matched_ids": ids}


def run_finalise(state: InputState) -> Dict[str, Any]:
    return finalise(state["preferences"], state["matched_ids"])


async def run_response_writer(state: InputState) -> Dict[str, Any]:
    message = await compose_response(
        state.get("type", "ai_reply"),
        state.get("response_context", {}),
        state.get("ids"),
        state.get("conversation_summary", ""),
        state.get("user_input", ""),
    )
    return {"message": message}


async def run_verifier(state: InputState) -> Dict[str, Any]:
    result = await verify_response(
        state.get("message"),
        state.get("response_context", {}),
        state.get("ids"),
    )
    score = float(result.get("score", 0.0))
    retries = state.get("verifier_retries", 0)
    if score < settings.VERIFIER_SCORE_THRESHOLD:
        retries += 1
    return {"verifier_score": score, "verifier_retries": retries}


def route_after_guardrails(state: InputState) -> str:
    if state.get("guardrails_blocked"):
        return END
    return "collect_preferences"


def route_after_verifier(state: InputState) -> str:
    score = state.get("verifier_score", 0.0)
    retries = state.get("verifier_retries", 0)
    if should_retry(score, retries, settings.VERIFIER_SCORE_THRESHOLD, settings.VERIFIER_MAX_RETRIES):
        return "compose_response"
    return END




graph = (
    StateGraph(InputState, output_schema=OutputState)
    .add_node("guardrails", guardrails_node)
    .add_node("collect_preferences", run_preferences)
    .add_node("filter_properties", run_filter)
    .add_node("finalise", run_finalise)
    .add_node("compose_response", run_response_writer)
    .add_node("verifier", run_verifier)
    .add_edge("__start__", "guardrails")
    .add_conditional_edges("guardrails", route_after_guardrails)
    .add_edge("collect_preferences", "filter_properties")
    .add_edge("filter_properties", "finalise")
    .add_edge("finalise", "compose_response")
    .add_edge("compose_response", "verifier")
    .add_conditional_edges("verifier", route_after_verifier)
    .compile(name="chat_graph")
)