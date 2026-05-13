from pydantic import BaseModel, Field
from langchain_core.tools import tool

class ClarifyInput(BaseModel):
    message: str = Field(description="The clarifying message or question to ask the user.")

@tool("ask_clarification", args_schema=ClarifyInput)
def ask_clarification(message: str) -> str:
    """Use this tool when you need more information from the user to narrow down the property search, or to simply reply to their non-search queries (like greetings). This tool will pause the agent loop and send the message back to the client."""
    return message
