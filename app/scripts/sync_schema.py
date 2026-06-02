import asyncio
from sqlalchemy import text
from app.database import engine
from app.layer6_data.models import Base
from app.config import settings

async def sync_schema():
    """
    ELITE STARTUP SCRIPT
    Ensures the vector extension is enabled and all ORM tables are created.
    Designed for clean-slate deployments.
    """
    async with engine.begin() as conn:
        print("Starting Elite System Initialization...")

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
            await conn.run_sync(Base.metadata.create_all)
            print("  [OK] All tables (Candidates, Resumes, Jobs, Versions, Memory, etc.) verified.")
        except Exception as e:
            print(f"  [ERROR] Schema synchronization failed: {e}")
            raise e

        # 3. Incremental column additions for existing tables (ALTER TABLE safe)
        print("- Applying incremental schema patches...")
        _patches = [
            # Jobs table: recruitment tracking columns
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS client_id VARCHAR REFERENCES clients(id)",
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS priority VARCHAR DEFAULT 'medium'",
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS target_count INTEGER DEFAULT 1",
            # Convert status/priority columns from native PostgreSQL ENUM to plain VARCHAR.
            # ::text cast works on any enum type regardless of values.
            "ALTER TABLE jobs ALTER COLUMN status TYPE VARCHAR USING status::text",
            "ALTER TABLE jobs ALTER COLUMN priority TYPE VARCHAR USING priority::text",
            "ALTER TABLE users ALTER COLUMN role TYPE VARCHAR USING role::text",
            "UPDATE users SET role = LOWER(role) WHERE role != LOWER(role)",
            # Resumes table: track which user uploaded each resume
            "ALTER TABLE resumes ADD COLUMN IF NOT EXISTS uploaded_by VARCHAR REFERENCES users(id)",
            # Interview invitations: link to job and recruiter for shortlisted tracking
            "ALTER TABLE interview_invitations ADD COLUMN IF NOT EXISTS job_id VARCHAR",
            "ALTER TABLE interview_invitations ADD COLUMN IF NOT EXISTS recruiter_id VARCHAR",
            # Performance indexes — critical for sub-200ms queries
            "CREATE INDEX IF NOT EXISTS idx_jobs_company_id ON jobs(company_id)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)",
            "CREATE INDEX IF NOT EXISTS idx_resumes_candidate_id ON resumes(candidate_id)",
            "CREATE INDEX IF NOT EXISTS idx_resumes_is_active ON resumes(is_active) WHERE is_active = TRUE",
            "CREATE INDEX IF NOT EXISTS idx_memories_company_id ON memories(company_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_resume_id ON memories(resume_id)",
            "CREATE INDEX IF NOT EXISTS idx_candidate_submissions_job_id ON candidate_submissions(job_id)",
            "CREATE INDEX IF NOT EXISTS idx_candidate_submissions_candidate_id ON candidate_submissions(candidate_id)",
            "CREATE INDEX IF NOT EXISTS idx_jd_assignments_employee_id ON jd_assignments(employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_jd_assignments_job_id ON jd_assignments(job_id)",
            # Assign orphaned users (NULL company_id, e.g. from Google OAuth sign-up) to the primary company
            "UPDATE users SET company_id = (SELECT id FROM companies ORDER BY created_at ASC LIMIT 1) WHERE company_id IS NULL",
            # Widen unique constraint: allow same candidate per job if submitted by different recruiters
            "ALTER TABLE candidate_submissions DROP CONSTRAINT IF EXISTS _job_email_uc",
            "ALTER TABLE candidate_submissions ADD CONSTRAINT _job_email_submitter_uc UNIQUE (job_id, candidate_email, submitted_by)",
        ]
        for patch in _patches:
            try:
                # Each patch runs in its own savepoint so a failure
                # doesn't abort the whole transaction
                await conn.execute(text("SAVEPOINT patch_sp"))
                await conn.execute(text(patch))
                await conn.execute(text("RELEASE SAVEPOINT patch_sp"))
            except Exception as e:
                await conn.execute(text("ROLLBACK TO SAVEPOINT patch_sp"))
                print(f"  [WARN] Patch skipped ({e})")
        print("  [OK] Schema patches applied.")

        # 4. Update company name / merge companies if COMPANY_NAME env var is customised
        if settings.COMPANY_NAME and settings.COMPANY_NAME != "Hirix Company":
            try:
                await conn.execute(text("SAVEPOINT company_sp"))

                # Check whether the target company already exists
                target_res = await conn.execute(
                    text("SELECT id FROM companies WHERE name = :name"),
                    {"name": settings.COMPANY_NAME}
                )
                target_row = target_res.fetchone()

                if target_row:
                    # Target company exists → merge ALL other companies' data into it
                    tid = target_row[0]
                    for tbl in ("users", "jobs", "memories", "candidate_submissions",
                                "notifications", "clients"):
                        try:
                            await conn.execute(
                                text(f"UPDATE {tbl} SET company_id = :tid WHERE company_id != :tid AND company_id IS NOT NULL"),
                                {"tid": tid}
                            )
                        except Exception:
                            pass  # table may not have company_id
                    # Also fix orphaned NULL company_id rows
                    await conn.execute(
                        text("UPDATE users SET company_id = :tid WHERE company_id IS NULL"),
                        {"tid": tid}
                    )
                    print(f"  [OK] Merged all companies/users into: {settings.COMPANY_NAME}")
                else:
                    # No target company yet — rename the old one
                    await conn.execute(
                        text("UPDATE companies SET name = :name WHERE name = 'Hirix Company'"),
                        {"name": settings.COMPANY_NAME}
                    )
                    print(f"  [OK] Company name updated to: {settings.COMPANY_NAME}")

                await conn.execute(text("RELEASE SAVEPOINT company_sp"))
            except Exception as e:
                await conn.execute(text("ROLLBACK TO SAVEPOINT company_sp"))
                print(f"  [WARN] Could not update company name: {e}")

        # 5. Bootstrap first admin — create or update
        if settings.FIRST_ADMIN_EMAIL and settings.FIRST_ADMIN_PASSWORD:
            try:
                import uuid as _uuid
                from app.layer7_crosscutting.security import PasswordHasher
                hashed = PasswordHasher.hash(settings.FIRST_ADMIN_PASSWORD)

                # Check if user already exists
                existing = await conn.execute(
                    text("SELECT id, company_id FROM users WHERE email = :email"),
                    {"email": settings.FIRST_ADMIN_EMAIL},
                )
                row = existing.fetchone()

                if row:
                    # User exists — just update role and password
                    await conn.execute(
                        text("UPDATE users SET role = 'admin', hashed_password = :pw WHERE email = :email"),
                        {"pw": hashed, "email": settings.FIRST_ADMIN_EMAIL},
                    )
                    print(f"  [OK] Admin updated: {settings.FIRST_ADMIN_EMAIL} — role=admin, password reset.")
                else:
                    # User doesn't exist — get or create a company first, then create user
                    company_row = await conn.execute(text("SELECT id FROM companies LIMIT 1"))
                    existing_company = company_row.fetchone()

                    if existing_company:
                        company_id = existing_company[0]
                    else:
                        company_id = str(_uuid.uuid4())
                        await conn.execute(
                            text("INSERT INTO companies (id, name) VALUES (:id, :name)"),
                            {"id": company_id, "name": "Hirix Company"},
                        )

                    user_id = str(_uuid.uuid4())
                    await conn.execute(
                        text("""
                            INSERT INTO users (id, email, hashed_password, first_name, last_name, role, company_id, is_active)
                            VALUES (:id, :email, :pw, 'Admin', 'User', 'admin', :cid, true)
                            ON CONFLICT (email) DO UPDATE SET role='admin', hashed_password=EXCLUDED.hashed_password
                        """),
                        {"id": user_id, "email": settings.FIRST_ADMIN_EMAIL, "pw": hashed, "cid": company_id},
                    )
                    print(f"  [OK] Admin created: {settings.FIRST_ADMIN_EMAIL}")

                print(f"  [WARN] Remove FIRST_ADMIN_PASSWORD from .env after first login.")
            except Exception as e:
                import traceback; traceback.print_exc()
                print(f"  [WARN] Could not bootstrap admin: {e}")

        print("\n[OK] System Initialization Complete! Ready for AI Ingestion.")

if __name__ == "__main__":
    asyncio.run(sync_schema())
