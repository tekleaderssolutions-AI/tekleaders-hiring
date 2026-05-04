import asyncio
from sqlalchemy import text
from app.database import engine

async def sync_schema():
    async with engine.begin() as conn:
        print("Checking for missing columns in 'candidates' table...")
        
        # Add 'summary' if missing
        try:
            await conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS summary TEXT"))
            print("- Column 'summary' verified/added.")
        except Exception as e:
            print(f"- Error adding 'summary': {e}")

        # Rename 'metadata' to 'candidate_metadata' if old column exists
        try:
            # Check if old column exists
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='candidates' AND column_name='metadata'"
            ))
            if result.fetchone():
                await conn.execute(text("ALTER TABLE candidates RENAME COLUMN metadata TO candidate_metadata"))
                print("- Column 'metadata' renamed to 'candidate_metadata'.")
            else:
                await conn.execute(text("ALTER TABLE candidates ADD COLUMN IF NOT EXISTS candidate_metadata JSONB DEFAULT '{}'"))
                print("- Column 'candidate_metadata' verified/added.")
        except Exception as e:
            print(f"- Error handling 'candidate_metadata': {e}")

        print("\nSchema sync complete!")

if __name__ == "__main__":
    asyncio.run(sync_schema())
