from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    APP_NAME: str = "Speech to Text API"
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002"
    ]
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    AUDIO_SAMPLE_RATE: int = 48000
    AUDIO_ENCODING: str = "MP3"
    LANGUAGE_CODE: str = "en-US"
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "english_db"
    DB_USER: str = "minamikouji"
    DB_PASSWORD: str = ""

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 