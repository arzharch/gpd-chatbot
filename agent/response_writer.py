import json
from typing import Any, Dict, List

from openai import AsyncOpenAI

from config import settings
from tools.prompt_loader import load_prompt


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _fallback_message(response_context: Dict[str, Any]) -> str:
    missing = response_context.get("missing_fields") or []
    if missing:
        return "Please share " + " and ".join(missing) + " so I can narrow the options."

    if response_context.get("no_matches"):
        return "I could not find matches with those filters. Would you like to adjust them?"

    return load_prompt("assistant_fallback").strip()


async def compose_response(
    response_type: str,
    response_context: Dict[str, Any],
    ids: List[str] | None,
    conversation_summary: str,
    user_input: str,
) -> str:
    system = load_prompt("assistant_system")
    payload = {
        "type": response_type,
        "response_context": response_context,
        "ids": ids or [],
        "conversation_summary": conversation_summary,
        "user_input": user_input,
    }

    response = await client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    try:
        data = json.loads(content)
        message = data.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    except json.JSONDecodeError:
        pass

    return _fallback_message(response_context)
