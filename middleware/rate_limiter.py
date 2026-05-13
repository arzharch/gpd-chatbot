from slowapi import Limiter
from slowapi.util import get_remote_address
from config import settings

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

def get_chat_rate_limit():
    return f"{settings.RATE_LIMIT_CHAT_PER_MINUTE}/minute"