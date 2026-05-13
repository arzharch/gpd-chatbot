import json
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class FinaliseInput(BaseModel):
    ids: list[str] = Field(description="The list of property IDs to recommend.")
    message: str = Field(description="The message to send to the user with the recommendations.")

@tool("finalise_recommendation", args_schema=FinaliseInput)
def finalise_recommendation(ids: list[str], message: str) -> str:
    """Use this tool when you have found the properties the user wants and are ready to finalize the recommendation. This tool ends the agent loop."""
    return json.dumps({"ids": ids, "message": message, "finalised": True})