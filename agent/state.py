from typing import Literal, TypedDict


class InputState(TypedDict):
    user_input: str
    session_id: str
    history: list[dict]

class OutputState(TypedDict):
    type: Literal["ai_reply", "ids"]
    message: str | None
    ids: list[int] | None




