
import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine

async def check():
    async with AsyncSession(engine) as session:
        # Check tables existence and counts via raw SQL to be 100% sure
        tables = ["candidates", "resumes", "memories", "agent_runs"]
        print("--- Database Diagnostics ---")
        for table in tables:
            try:
                res = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res.scalar()
                print(f"Table '{table}': {count} records")
            except Exception as e:
                print(f"Table '{table}': ERROR (Does it exist?) - {str(e)}")

        # Check if there are any resumes for the last 10 minutes
        try:
            res = await session.execute(text("SELECT id, email, first_name, last_name FROM candidates ORDER BY created_at DESC LIMIT 10"))
            rows = res.all()
            print("\n--- Latest 10 Candidates ---")
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error fetching candidates: {e}")

if __name__ == "__main__":
    asyncio.run(check())
