from tools.query_properties import query_properties
from tools.clarify import ask_clarification
from tools.shortlist import add_to_shortlist, remove_from_shortlist
from tools.compare import compare_properties
from tools.finalise import finalise_recommendation

TOOLS = [
    query_properties,
    ask_clarification,
    add_to_shortlist,
    remove_from_shortlist,
    compare_properties,
    finalise_recommendation
]
