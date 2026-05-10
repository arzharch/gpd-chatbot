import json
from typing import Any, Dict, List


def _matches_text(haystack: str, needle: str) -> bool:
    return needle.lower() in haystack.lower()


def _load_listings(listings_path: str) -> List[Dict[str, Any]]:
    with open(listings_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def filter_properties(preferences: Dict[str, Any], listings_path: str) -> List[str]:
    listings = _load_listings(listings_path)

    results: List[str] = []
    for item in listings:
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