from typing import Dict, List


# In-Memory Memory Store : session_id -> messages

_memory: Dict[str, List[dict]] = {}

def get_memory(session_id : str) -> List[dict]:
    """Return history for a session, or empty list if new."""
    return _memory.get(session_id, []).copy()


def save_memory(session_id : str, messages : List[dict]) -> None:
    """Save history for a session."""
    _memory[session_id] = messages.copy()