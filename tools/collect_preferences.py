import json
import re
from typing import Optional, Dict, Any

from openai import AsyncOpenAI

from config import settings
from tools.prompt_loader import load_prompt


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

    match = re.search(r"(under|below|upto|up to|less than)\s*(\d+)\s*(cr|crore)", t)
    if match:
        num = match.group(2)
        if num == "5":
            return "under-5cr"
        if num == "15":
            return "under-15cr"
        if num == "25":
            return "under-25cr"

    match = re.search(r"(around|about|approx|approximately|range of|budget of|budget)\s*(\d+)\s*(cr|crore)", t)
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


def _extract_type_rule(text: str) -> Optional[str]:
    t = _normalize(text)
    if re.search(r"\b(apartment|apartments|flat|flats)\b", t):
        return "APARTMENT"
    if re.search(r"\b(villa|villas)\b", t):
        return "VILLA"
    if re.search(r"\b(land|plot|plots)\b", t):
        return "LAND"
    return None


def _last_assistant_message(history: list[dict] | None) -> str:
    if not history:
        return ""
    for item in reversed(history):
        if item.get("role") == "assistant":
            return (item.get("content") or "").strip()
    return ""


async def _extract_with_llm(text: str, summary: str | None, history: list[dict] | None) -> Dict[str, Any]:
    """
    LLM zero-shot extraction. Returns a JSON dict with keys:
    type, location, beds, club_id, furnished, pool, zone_type
    """
    system = load_prompt("extractor_system")

    payload = {
        "user_input": text,
        "conversation_summary": summary or "",
        "last_assistant_message": _last_assistant_message(history),
    }
    user = json.dumps(payload)

    response = await client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}


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

    prop_type = _extract_type_rule(text)
    if prefs["type"] is None and prop_type is not None:
        prefs["type"] = prop_type

    # Normalize type if user uses lowercase
    if isinstance(prefs["type"], str):
        prefs["type"] = prefs["type"].upper()

    return prefs


async def collect_preferences(text: str, summary: str | None = None, history: list[dict] | None = None) -> Dict[str, Any]:
    """
    Main function to call from your graph.
    1) LLM extraction
    2) Rule-based validation/patch
    """
    llm_prefs = await _extract_with_llm(text, summary, history)
    return _validate_and_merge(llm_prefs, text)