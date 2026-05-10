import json
import re
from typing import Optional, Dict, Any

from openai import AsyncOpenAI
from config import settings


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _normalize(text: str) -> str:
    return text.lower().strip()


def _extract_beds_rule(text: str) -> Optional[int]:
    # catches "2 bhk", "3 bedroom", "4 bed"
    match = re.search(r"\b(\d+)\s*(bhk|bed|bedroom|beds)\b", _normalize(text))
    if match:
        return int(match.group(1))
    return None


def _extract_club_id_rule(text: str) -> Optional[str]:
    t = _normalize(text)

    match = re.search(r"(under|below|upto|up to)\s*(\d+)\s*(cr|crore)", t)
    if match:
        num = match.group(2)
        if num == "5":
            return "under-5cr"
        if num == "15":
            return "under-15cr"
        if num == "25":
            return "under-25cr"

    match = re.search(r"\b(5|15|25)\s*(cr|crore)\b", t)
    if match:
        num = match.group(1)
        if num == "5":
            return "under-5cr"
        if num == "15":
            return "under-15cr"
        if num == "25":
            return "under-25cr"

    return None


async def _extract_with_llm(text: str) -> Dict[str, Any]:
    """
    LLM zero-shot extraction. Returns a JSON dict with keys:
    type, location, beds, club_id, furnished, pool, zone_type
    """
    system = (
        "You are an extraction engine. Return ONLY valid JSON.\n"
        "Extract real estate preferences from user text.\n"
        "Keys: type, location, beds, club_id, furnished, pool, zone_type.\n"
        "Allowed type values: APARTMENT, VILLA, LAND, or null.\n"
        "club_id must be one of: under-5cr, under-15cr, under-25cr, or null.\n"
        "beds must be integer or null. pool must be true/false/null.\n"
        "If unknown, use null."
    )

    user = f"User text: {text}"

    response = await client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def _validate_and_merge(llm_prefs: Dict[str, Any], text: str) -> Dict[str, Any]:
    """
    Merge LLM output with rule-based signals.
    Rule-based values win if LLM is missing or inconsistent.
    """
    prefs = {
        "type": llm_prefs.get("type"),
        "location": llm_prefs.get("location"),
        "beds": llm_prefs.get("beds"),
        "club_id": llm_prefs.get("club_id"),
        "furnished": llm_prefs.get("furnished"),
        "pool": llm_prefs.get("pool"),
        "zone_type": llm_prefs.get("zone_type"),
    }

    # Override/patch with rules if missing
    beds = _extract_beds_rule(text)
    if prefs["beds"] is None and beds is not None:
        prefs["beds"] = beds

    club_id = _extract_club_id_rule(text)
    if prefs["club_id"] is None and club_id is not None:
        prefs["club_id"] = club_id

    # Normalize type if user uses lowercase
    if isinstance(prefs["type"], str):
        prefs["type"] = prefs["type"].upper()

    return prefs


async def collect_preferences(text: str) -> Dict[str, Any]:
    """
    Main function to call from your graph.
    1) LLM extraction
    2) Rule-based validation/patch
    """
    llm_prefs = await _extract_with_llm(text)
    return _validate_and_merge(llm_prefs, text)