import json
from typing import Any, Dict, List


DATA_PATH= r"C:\Users\arshc\Desktop\gpd-chatbot\data\properties.json"

def _load_properties() -> List[Dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf=8") as f:
        return json.load(f)


def _matches_text(haystack: str, needle: str) -> bool:
    return needle.lower() in haystack.lower()

def filter_properties(preferences: Dict[str, Any]) -> List[str]:
    """
    Filter properties based on available preferences.
    Only apply filters for values that are not None.
    Returns a list of matching IDs as strings (since your IDs are strings).
    """

    properties = _load_properties()

    results = []
    for item in properties:
        if preferences.get("type") and item.get("type") != preferences["type"]:
            continue

        if preferences.get("beds") is not None:
            if item.get("beds") is None or item.get("beds") != preferences["beds"]:
                continue

        if preferences.get("club_id") and item.get("club_id") != preferences["club_id"]:
            continue

        if preferences.get("location"):
            if not item.get("location") or not _matches_text(item["location"], preferences["location"]):
                continue

        if preferences.get("furnished"):
            if item.get("furnished") != preferences["furnished"]:
                continue

        if preferences.get("pool") is not None:
            if item.get("pool") != preferences["pool"]:
                continue

        if preferences.get("zone_type"):
            if item.get("zone_type") != preferences["zone_type"]:
                continue

        results.append(item["id"])

    return results
