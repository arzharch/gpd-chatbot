from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

from typing import Dict, Any

from dataclasses import dataclass


class Context(TypedDict):
    my_configurable_param: str


@dataclass
class State:

    """
    Inpuy state for the agent.
    Defines initial structure of the incoming data
    
    """

    change_me:str ="example"


async def call_model(state: State, runtime: Runtime[Context]) -> Dict[str,Any]:
    """
    This is the function that will be called by the agent.
    It takes in the current state and the runtime, and returns a dictionary of outputs.
    """

    # Example of how to access the context
    my_configurable_param = runtime.context.my_configurable_param

    # Example of how to access the state
    change_me = state.change_me

    # Here you would call your model with the appropriate inputs and get the outputs
    # For this example, we'll just return a dummy output
    output = {"output": f"Model called with change_me: {change_me} and my_configurable_param: {my_configurable_param}"}

    return output

# Define the graph
graph= (StateGraph(State, context_schema=Context)
        .add_node(call_model)
        .add_edge("__start__", "call_model")
        .compile(name="New Graph")
        )