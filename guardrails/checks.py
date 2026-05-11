from typing import Tuple

from guardrails.patterns import NSFW, PROMPT_INJECTION, SQL_INJECTION


def _matches_any(patterns, text: str) -> bool:
	return any(p.search(text) for p in patterns)


def run_all_checks(text: str) -> Tuple[bool, str | None]:
	if _matches_any(PROMPT_INJECTION, text):
		return False, "I can’t help with that request."
	if _matches_any(SQL_INJECTION, text):
		return False, "I can’t process that input."
	if _matches_any(NSFW, text):
		return False, "I can’t help with that request."
	return True, None
