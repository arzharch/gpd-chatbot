from typing import Any, Dict

from langgraph.graph import StateGraph

from agent.state import InputState, OutputState
from tools.collect_preferences import collect_preferences
from tools.compare import filter_properties
from tools.finalise import finalise


async def run_preferences(state: InputState) -> Dict[str, Any]:
    prefs = await collect_preferences(state["user_input"])
    return {"preferences": prefs}


def run_filter(state: InputState) -> Dict[str, Any]:
    ids = filter_properties(state["preferences"], state["listings_path"])
    return {"matched_ids": ids}


def run_finalise(state: InputState) -> Dict[str, Any]:
    return finalise(state["preferences"], state["matched_ids"])




graph = (
    StateGraph(InputState, output_schema=OutputState)
    .add_node("collect_preferences", run_preferences)
    .add_node("filter_properties", run_filter)
    .add_node("finalise", run_finalise)
    .add_edge("__start__", "collect_preferences")
    .add_edge("collect_preferences", "filter_properties")
    .add_edge("filter_properties", "finalise")
    .compile(name="chat_graph")
)