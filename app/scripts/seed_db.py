"""
scripts/seed_db.py
Seed the database with demo data for development.

Usage:
    python -m app.scripts.seed_db
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import app.layer6_data.models  # noqa: F401 - registers all models
from app.layer6_data.models import Base
from app.layer6_data.models.company_model import CompanyModel, CompanySize, CompanyStatus
from app.layer6_data.models.user_model import UserModel, UserRole
from app.layer7_crosscutting.security import PasswordHasher
from app.config import settings

async def seed():
    engine = create_async_engine(settings.async_database_url, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            company_id = str(uuid.uuid4())
            company = CompanyModel(
                id=company_id,
                name="Hirix Demo Corp",
                industry="Technology",
                size=CompanySize.STARTUP,
                status=CompanyStatus.ACTIVE,
            )
            session.add(company)

            admin = UserModel(
                id=str(uuid.uuid4()),
                company_id=company_id,
                email="admin@hirix.ai",
                hashed_password=PasswordHasher.hash("Admin@1234"),
                first_name="Admin",
                last_name="User",
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin)

        print("✅ Seed data inserted: company + admin user")
        print("   Email: admin@hirix.ai | Password: Admin@1234")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
