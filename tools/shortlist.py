import json
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class ShortlistInput(BaseModel):
    ids: list[str] = Field(description="A list of property IDs to add or remove.")

@tool("add_to_shortlist", args_schema=ShortlistInput)
def add_to_shortlist(ids: list[str]) -> str:
    """Use this tool to add specific property IDs to the user's shortlist."""
    return json.dumps({"action": "add", "ids": ids, "status": "success"})

@tool("remove_from_shortlist", args_schema=ShortlistInput)
def remove_from_shortlist(ids: list[str]) -> str:
    """Use this tool to remove specific property IDs from the user's shortlist."""
    return json.dumps({"action": "remove", "ids": ids, "status": "success"})
