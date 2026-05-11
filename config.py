from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY : str
    MODEL_NAME : str
    SUPABASE_URL : str
    SUPABASE_SERVICE_ROLE_KEY : str
    PROMPTS_DIR : str = "prompts"
    VERIFIER_SCORE_THRESHOLD : float = 0.8
    VERIFIER_MAX_RETRIES : int = 1
    SUMMARY_MAX_CHARS : int = 1200

    class Config:
        env_file=".env"


settings = Settings()
        