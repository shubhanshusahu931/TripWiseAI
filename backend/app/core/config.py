import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8080,http://127.0.0.1:8080"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # AI Configuration
    AI_PROVIDER: str = "gemini"  # "gemini", "openai", "groq", "openrouter", "mock"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-1.5-flash"
    AI_BASE_URL: str = ""

    # Local SQLite fallback database path
    LOCAL_DB_PATH: str = "tripwise_local.db"

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        origins = [orig.strip() for orig in self.CORS_ORIGINS.split(",") if orig.strip()]
        return origins if origins else ["*"]

    model_config = {"env_file": ".env", "extra": "allow"}

settings = Settings()
