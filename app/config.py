from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Hirix Recruitment API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/hirix"

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

    # OpenAI / LLM
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    from pydantic_settings import SettingsConfigDict
    import os
    from pathlib import Path
    
    # Absolute path to .env file
    _env_path = os.path.join(Path(__file__).parent.parent, ".env")
    
    model_config = SettingsConfigDict(
        env_file=_env_path,
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()

# Safety Check (Redacted print)
if settings.OPENAI_API_KEY:
    print(f"✅ OpenAI Key detected (Starts with: {settings.OPENAI_API_KEY[:7]}...)")
else:
    print("❌ CRITICAL: OpenAI API Key NOT FOUND in environment or .env file!")
