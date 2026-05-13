from typing import Any, Dict, List, Literal, TypedDict, Annotated
import operator
from pydantic import BaseModel, Field

class Preferences(BaseModel):
    type: str | None = None
    location: str | None = None
    beds: int | None = None
    club_id: str | None = None
    furnished: bool | None = None
    pool: bool | None = None
    zone_type: str | None = None

class AgentState(TypedDict):
    session_id: str
    messages: Annotated[list, operator.add]
    shortlist: List[str]
    preferences: Preferences
    confidence: float
    verifier_reason: str | None
    next_action: str | None
    listings_path: str
    conversation_summary: str
    final_response: Dict[str, Any] | None

