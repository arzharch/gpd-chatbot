from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import json

class QueryPropertiesInput(BaseModel):
    listings_path: str = Field(description="The path to the listings JSON file. Always pass the path from the state.")
    property_type: Optional[str] = Field(None, description="The type of property: APARTMENT, VILLA, or LAND")
    location: Optional[str] = Field(None, description="The location to search for.")
    beds: Optional[int] = Field(None, description="Number of bedrooms (BHK).")
    club_id: Optional[str] = Field(None, description="Budget club: under-5cr, under-15cr, under-25cr")
    furnished: Optional[bool] = Field(None, description="Whether the property is furnished.")

def _matches_text(haystack: str, needle: str) -> bool:
    return needle.lower() in haystack.lower()

@tool("query_properties", args_schema=QueryPropertiesInput)
def query_properties(
    listings_path: str,
    property_type: Optional[str] = None,
    location: Optional[str] = None,
    beds: Optional[int] = None,
    club_id: Optional[str] = None,
    furnished: Optional[bool] = None
) -> str:
    """Queries the local listings JSON file to find matching properties."""
    try:
        with open(listings_path, "r", encoding="utf-8") as f:
            listings = json.load(f)
    except FileNotFoundError:
        return json.dumps({"error": f"Listings file {listings_path} not found."})

    results = []
    for item in listings:
        if property_type and item.get("type") != property_type:
            continue
        if beds is not None and item.get("beds") != beds:
            continue
        if club_id and item.get("club_id") != club_id:
            continue
        if location and (not item.get("location") or not _matches_text(item["location"], location)):
            continue
        if furnished is not None and item.get("furnished") != furnished:
            continue
        
        # Include minimal details to avoid huge context
        results.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "type": item.get("type"),
            "location": item.get("location"),
            "beds": item.get("beds"),
            "club_id": item.get("club_id"),
            "furnished": item.get("furnished"),
            "description": item.get("description")
        })

    return json.dumps({"matched_count": len(results), "matches": results})
