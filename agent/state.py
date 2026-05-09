from typing import Literal, TypedDict


class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    type: Literal["ai_reply", "ids"]
    message: str | None
    ids: list[int] | None




