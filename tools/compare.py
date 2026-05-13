import json
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CompareInput(BaseModel):
    ids: list[str] = Field(description="List of property IDs to compare.")
    listings_path: str = Field(description="The path to the listings JSON file. Always pass the path from the state.")

@tool("compare_properties", args_schema=CompareInput)
def compare_properties(ids: list[str], listings_path: str) -> str:
    """Use this tool to get detailed information about specific properties to compare them for the user."""
    try:
        with open(listings_path, "r", encoding="utf-8") as f:
            listings = json.load(f)
    except FileNotFoundError:
        return json.dumps({"error": f"Listings file {listings_path} not found."})

    results = []
    for item in listings:
        if item.get("id") in ids:
            results.append(item)
            
    if not results:
        return json.dumps({"error": "No matching properties found for the given IDs."})
        
    return json.dumps({"compared_properties": results})