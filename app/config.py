from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hirix AI"
    ENVIRONMENT: str = "development"
    
    # API Settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/hirix"
    
    # AI Settings
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Vector DB Settings
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""
    
    # Messaging
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
