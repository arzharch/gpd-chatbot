import json
from typing import Any, Dict
from openai import AsyncOpenAI
from config import settings
from tools.prompt_loader import load_prompt
from agent.state import AgentState

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

async def verifier_node(state: AgentState) -> Dict[str, Any]:
    final_response = state.get("final_response")
    if not final_response:
        # If there's no final response (e.g. tools just updated state), we don't verify yet
        return {}

    system = load_prompt("verifier_system")
    payload = {
        "final_response": final_response,
        "history": state["messages"][-5:],
        "shortlist": state["shortlist"]
    }

    try:
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
        score = _to_float(data.get("score"))
        reason = data.get("reason", "")
        
        if score < settings.VERIFIER_SCORE_THRESHOLD:
            # Revert final response and send reason back
            return {
                "verifier_reason": reason,
                "final_response": None,
                "messages": [{"role": "system", "content": f"Verifier rejected the previous response: {reason}. Please correct it."}]
            }
        else:
            return {"verifier_reason": None}
            
    except Exception as e:
        # On error, pass it through to not break the app
        return {"verifier_reason": None}
