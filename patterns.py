import re

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore\s+previous\s+instructions"),
    re.compile(r"(?i)disregard\s+all\s+prior\s+messages"),
    re.compile(r"(?i)forget\s+everything\s+said\s+before"),
    re.compile(r"system prompt", re.I),
    re.compile(r"developer message", re.I),
    re.compile(r"reveal.*(policy|prompt)", re.I),

]


SQL_INJECTION_PATTERNS = [
    re.compile(r"(?i)union\s+select"),
    re.compile(r"(?i)select\s+.*\s+from\s+"),
    re.compile(r"(?i)insert\s+into\s+"),
    re.compile(r"\bdrop\b|\btruncate\b|\bdelete\b", re.I),
    re.compile(r"(--|;|/\*|\*/)", re.I),
]    

NSFW = [
    re.compile(r"\bsex\b|\bporn\b|\bnude\b", re.I),
    re.compile(r"\berotic\b|\bexplicit\b", re.I),
]