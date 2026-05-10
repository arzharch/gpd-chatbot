from datetime import datetime
from pydantic import BaseModel
from typing import Any, Literal

class ChatResponse(BaseModel):
    type: Literal["ai_reply", "ids"]
    message: str | None = None
    ids: list[str] | None = None


class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime
    metadata: dict[str, Any] | None = None