import json
import os
import re
from typing import Any, Dict, List


SESSION_DIR = os.path.join("data", "sessions")
_SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_-]")


def _safe_session_id(session_id: str) -> str:
    cleaned = _SAFE_ID_RE.sub("_", session_id)
    return cleaned[:64] if cleaned else "session"


def write_session_listings(session_id: str, listings: List[Dict[str, Any]]) -> str:
    os.makedirs(SESSION_DIR, exist_ok=True)
    safe_id = _safe_session_id(session_id)
    path = os.path.join(SESSION_DIR, f"{safe_id}.json")

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(listings, handle)

    return path
