import asyncio
from sqlalchemy import text
from app.database import engine

async def sync_schema():
    async with engine.begin() as conn:
        print("Starting comprehensive schema synchronization for 'candidates' table...")
        
        columns_to_add = [
            ("summary", "TEXT"),
            ("skills", "JSONB DEFAULT '[]'"),
            ("experience", "JSONB DEFAULT '[]'"),
            ("education", "JSONB DEFAULT '[]'"),
            ("total_years_experience", "FLOAT DEFAULT 0.0"),
            ("memory_id", "VARCHAR"),
            ("candidate_metadata", "JSONB DEFAULT '{}'"),
            ("first_name", "VARCHAR"),
            ("last_name", "VARCHAR"),
            ("phone", "VARCHAR"),
            ("location", "VARCHAR")
        ]

        for col_name, col_type in columns_to_add:
            try:
                await conn.execute(text(f"ALTER TABLE candidates ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"- Column '{col_name}' ({col_type}) verified/added.")
            except Exception as e:
                print(f"- Error adding '{col_name}': {e}")

        # Rename 'metadata' to 'candidate_metadata' if old column exists
        try:
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='candidates' AND column_name='metadata'"
            ))
            if result.fetchone():
                await conn.execute(text("ALTER TABLE candidates RENAME COLUMN metadata TO candidate_metadata"))
                print("- Column 'metadata' renamed to 'candidate_metadata'.")
        except Exception as e:
            print(f"- Error renaming 'metadata': {e}")

        print("\nSchema sync complete!")

if __name__ == "__main__":
    asyncio.run(sync_schema())
