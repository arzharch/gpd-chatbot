import json
from typing import Any, Dict

from openai import AsyncOpenAI

from config import settings
from tools.prompt_loader import load_prompt


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


async def verify_response(
    message: str | None,
    response_context: Dict[str, Any] | None,
    ids: list[str] | None,
) -> Dict[str, Any]:
    system = load_prompt("verifier_system")
    payload = {
        "message": message or "",
        "response_context": response_context or {},
        "ids": ids or [],
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
    data = json.loads(content)
    return {
        "score": _to_float(data.get("score")),
        "reason": data.get("reason", ""),
    }
