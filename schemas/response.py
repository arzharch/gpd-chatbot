from datetime import datetime
from pydantic import BaseModel, TypeAdapter
from typing import Annotated, Any, Literal, Union
from pydantic import Discriminator, Tag

class AIReply(BaseModel):
    type: Literal["ai_reply"] = "ai_reply"
    message: str

class IDsResponse(BaseModel):
    type: Literal["ids"] = "ids"
    ids: list[str]

ChatResponse = Annotated[
    Union[
        Annotated[AIReply, Tag("ai_reply")],
        Annotated[IDsResponse, Tag("ids")],
    ],
    Discriminator("type"),
]

ChatResponseAdapter = TypeAdapter(ChatResponse)

def parse_chat_response(data: dict) -> AIReply | IDsResponse:
    """Validate a dict into the correct ChatResponse variant."""
    return ChatResponseAdapter.validate_python(data)

class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime
    metadata: dict[str, Any] | None = None