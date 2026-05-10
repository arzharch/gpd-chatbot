from pydantic import BaseModel
from typing import Literal

class ChatResponse(BaseModel):
    type: Literal["ai_reply", "ids"]
    message: str | None = None
    ids: list[str] | None = None