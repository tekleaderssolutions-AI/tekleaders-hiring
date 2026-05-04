import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings
import app.layer6_data.models  # noqa: F401
from app.layer6_data.models import Base

async def reset_database():
    print("WARNING: This will drop ALL tables and delete ALL data.")
    confirm = input("Are you sure you want to proceed? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return

    engine = create_async_engine(settings.async_database_url, echo=True)
    async with engine.begin() as conn:
        # 1. Enable vector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        # 2. Drop all tables
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        
        # 3. Create all tables
        print("Creating all tables fresh...")
        await conn.run_sync(Base.metadata.create_all)
        
    await engine.dispose()
    print("\nOK: Database reset successfully with the new schema!")

if __name__ == "__main__":
    asyncio.run(reset_database())
