from typing import Any, Dict, List

def _missing_key_fields(prefs: Dict[str, Any]) -> List[str]:
    missing = []

    if not prefs.get("type"):
        missing.append("property type (apartment, villa, or land)")

    if not prefs.get("club_id"):
        missing.append("budget range (under 5 cr, 15  cr or 25 cr)")

    return missing

def finalise(preferences: Dict[str, Any], ids: List[str]) -> Dict[str, Any]:
    """Decide whether to ask for clarification or return matching IDs."""

    missing = _missing_key_fields(preferences)
    response_context = {
        "missing_fields": missing,
        "matched_count": len(ids),
        "has_matches": bool(ids),
        "no_matches": not ids and not missing,
        "preferences": {key: value for key, value in preferences.items() if value is not None},
    }

    if missing:
        return {
            "type": "ai_reply",
            "message": None,
            "ids": None,
            "response_context": response_context,
        }

    if not ids:
        return {
            "type": "ai_reply",
            "message": None,
            "ids": None,
            "response_context": response_context,
        }

    return {
        "type": "ids",
        "message": None,
        "ids": ids,
        "response_context": response_context,
    }