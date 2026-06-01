from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json
import os
from pathlib import Path

# Absolute path to .env file
_env_path = os.path.join(Path(__file__).parent.parent, ".env")

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Hirix Recruitment API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/hirix"
    DATABASE_SSL: bool = False  # Set True for Neon / any cloud PostgreSQL

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL

    # JWT
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/gmail/callback"
    GOOGLE_REFRESH_TOKEN: str = ""
    GOOGLE_SENDER_EMAIL: str = ""

    # OpenAI / LLM
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Bootstrap admin — set to your email to promote that user to admin on startup
    FIRST_ADMIN_EMAIL: str = ""
    # Optionally reset the admin password on startup (clear after use)
    FIRST_ADMIN_PASSWORD: str = ""

    # AWS S3 (optional — for resume file storage)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # CORS — accepts JSON array or comma-separated string from env vars
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=_env_path,
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()

# Safety Check (Redacted print)
if settings.OPENAI_API_KEY:
    print(f"OK: OpenAI Key detected (Starts with: {settings.OPENAI_API_KEY[:7]}...)")
else:
    print("ERROR: CRITICAL: OpenAI API Key NOT FOUND in environment or .env file!")
