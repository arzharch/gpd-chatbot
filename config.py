from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY : str
    MODEL_NAME : str = "gpt-4.1-nano-2025-04-14"
    SUPABASE_URL : str
    SUPABASE_ANON_KEY : str
    SUPABASE_SERVICE_ROLE_KEY : str
    PROMPTS_DIR : str = "prompts"
    VERIFIER_SCORE_THRESHOLD : float = 0.8
    VERIFIER_MAX_RETRIES : int = 1
    SUMMARY_MAX_CHARS : int = 1200
    ALLOWED_ORIGINS : List[str]
    RATE_LIMIT_CHAT_PER_MINUTE : int



    class Config:
        env_file=".env"


settings = Settings()
