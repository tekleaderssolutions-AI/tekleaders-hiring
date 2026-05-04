"""
scripts/create_tables.py
Run once to create all database tables defined in the ORM models.

Usage:
    python -m app.scripts.create_tables
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
import app.layer6_data.models  # noqa: F401 — ensures all models are registered with Base

from app.layer6_data.models import Base

async def create_all_tables():
    engine = create_async_engine(settings.async_database_url, echo=True)
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Enable pgvector extension before creating tables
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("OK: All tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_all_tables())
