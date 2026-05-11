import json

from openai import AsyncOpenAI

from config import settings
from tools.prompt_loader import load_prompt


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _clip_summary(summary: str) -> str:
    limit = settings.SUMMARY_MAX_CHARS
    return summary[:limit] if len(summary) > limit else summary


async def update_summary(previous_summary: str | None, user_input: str, assistant_reply: str) -> str:
    system = load_prompt("summary_system")
    payload = {
        "previous_summary": previous_summary or "",
        "user_input": user_input,
        "assistant_reply": assistant_reply,
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
        summary = data.get("summary", "")
        if isinstance(summary, str) and summary.strip():
            return _clip_summary(summary.strip())
    except json.JSONDecodeError:
        pass

    return _clip_summary(previous_summary or "")
