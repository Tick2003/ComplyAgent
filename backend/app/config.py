"""Application configuration via environment variables."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from environment / .env file."""

    APP_NAME: str = "ComplyAgent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./complyagent.db"

    # LLM - Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # Auth (mock)
    SECRET_KEY: str = "complyagent-hackathon-secret-key-2025"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # File storage
    UPLOAD_DIR: str = "./data/circulars"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
