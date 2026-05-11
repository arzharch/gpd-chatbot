import re


REAL_ESTATE_KEYWORDS = {
	"apartment",
	"villa",
	"land",
	"plot",
	"property",
	"home",
	"house",
	"place",
	"bed",
	"bhk",
	"budget",
	"price",
	"location",
	"buy",
	"sell",
	"rent",
	"goa",
}

_BHK_RE = re.compile(r"\b\d+\s*bhk\b", re.I)
_BUDGET_RE = re.compile(r"\b(under|below|upto|up to|less than)\s*\d+\s*(cr|crore)\b", re.I)
_CRORE_RE = re.compile(r"\b\d+\s*(cr|crore)\b", re.I)


def is_real_estate_topic(text: str) -> bool:
	lowered = text.lower()
	if _BHK_RE.search(lowered):
		return True
	if _BUDGET_RE.search(lowered) or _CRORE_RE.search(lowered):
		return True
	return any(word in lowered for word in REAL_ESTATE_KEYWORDS)
