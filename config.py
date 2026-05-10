from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY : str
    MODEL_NAME : str
    SUPABASE_URL : str
    SUPABASE_SERVICE_ROLE_KEY : str

    class Config:
        env_file=".env"


settings = Settings()
        