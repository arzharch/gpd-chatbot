import re

PROMPT_INJECTION = [
	re.compile(r"ignore (all|previous) instructions", re.I),
	re.compile(r"system prompt", re.I),
	re.compile(r"developer message", re.I),
	re.compile(r"reveal.*(policy|prompt)", re.I),
]

SQL_INJECTION = [
	re.compile(r"\bselect\b.*\bfrom\b", re.I),
	re.compile(r"\bdrop\b|\btruncate\b|\bdelete\b", re.I),
	re.compile(r"(--|;|/\*|\*/)", re.I),
]

NSFW = [
	re.compile(r"\bsex\b|\bporn\b|\bnude\b", re.I),
	re.compile(r"\berotic\b|\bexplicit\b", re.I),
]
