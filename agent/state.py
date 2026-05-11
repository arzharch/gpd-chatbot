from typing import Literal, TypedDict


class InputState(TypedDict):
    user_input: str
    session_id: str
    history: list[dict]
    conversation_summary: str
    preferences: dict
    matched_ids: list[str]
    listings_path: str
    guardrails_blocked: bool
    verifier_score: float | None
    verifier_retries: int
    response_context: dict
    message: str | None
    ids: list[str] | None


class OutputState(TypedDict):
    type: Literal["ai_reply", "ids"]
    message: str | None
    ids: list[str] | None




