import asyncio
from sqlalchemy import text
from app.database import engine
from app.layer6_data.models import Base

async def sync_schema():
    """
    ELITE STARTUP SCRIPT
    Ensures the vector extension is enabled and all ORM tables are created.
    Designed for clean-slate deployments.
    """
    async with engine.begin() as conn:
        print("🚀 Starting Elite System Initialization...")
        
        # 1. Enable Vector Extension (Critical for pgvector)
        try:
            print("- Enabling 'vector' extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            print("  [OK] Vector extension verified.")
        except Exception as e:
            print(f"  [ERROR] Failed to enable vector extension: {e}")
            raise e

        # 2. Create All Tables from Registry
        try:
            print("- Synchronizing ORM Models with Database...")
            # Note: run_sync is used to bridge async SQLAlchemy with sync Base.metadata
            await conn.run_sync(Base.metadata.create_all)
            print("  [OK] All tables (Candidates, Resumes, Jobs, Versions, Memory, etc.) verified.")
        except Exception as e:
            print(f"  [ERROR] Schema synchronization failed: {e}")
            raise e

        print("\n✅ System Initialization Complete! Ready for AI Ingestion.")

if __name__ == "__main__":
    asyncio.run(sync_schema())
