from typing import Any, Dict

from guardrails.checks import run_all_checks


def guardrails_node(state: Dict[str, Any]) -> Dict[str, Any]:
	ok, message = run_all_checks(state["user_input"])
	if not ok:
		return {
			"guardrails_blocked": True,
			"type": "ai_reply",
			"message": message,
			"ids": None,
		}
	return {"guardrails_blocked": False}


__all__ = ["guardrails_node"]
