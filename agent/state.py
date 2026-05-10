from typing import Literal, TypedDict


class InputState(TypedDict):
    user_input: str
    session_id: str
    history: list[dict]
    preferences: dict
    matched_ids: list[str]
    listings_path: str


class OutputState(TypedDict):
    type: Literal["ai_reply", "ids"]
    message: str | None
    ids: list[str] | None




