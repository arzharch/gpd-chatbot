import re
from functools import lru_cache
from pathlib import Path

from config import settings


_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


@lru_cache
def load_prompt(name: str) -> str:
    if not _NAME_RE.match(name):
        raise ValueError("Invalid prompt name")

    base = Path(settings.PROMPTS_DIR).resolve()
    path = (base / f"{name}.txt").resolve()

    if base not in path.parents and path.parent != base:
        raise ValueError("Invalid prompt path")

    return path.read_text(encoding="utf-8")
