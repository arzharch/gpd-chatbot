from typing import Any, Dict, List

def _missing_key_fields(prefs: Dict[str, Any]) -> List[str]:
    missing = []

    if not prefs.get("type"):
        missing.append("property type (apartment, villa, or land)")

    if not prefs.get("club_id"):
        missing.append("budget range (under 5 cr, 15  cr or 25 cr)")

    return missing

def finalise(preferences: Dict[str, Any], ids: List[str]) -> Dict[str, Any]:
    """
    Decide whether to ask for clarification or return matching IDs.
    """

    missing = _missing_key_fields(preferences)

    if missing:
        question = "To help you find the best properties, could you please provide your " + " and ".join(missing) + "?"

        return{
            "type": "ai_reply",
            "message": question,
            "ids": None,    
        }
    
    if not ids:
        return {
            "type": "ai_reply",
            "message": "Sorry, I couldn't find any properties matching your preferences. Could you please adjust your criteria?",
            "ids": None,
        }
    
    return {
        "type": "ids",
        "message": "Here are the best matches based on what you shared.",
        "ids": ids,
    }