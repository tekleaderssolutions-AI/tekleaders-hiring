from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, update
from app.layer6_data.models.jd.job_model import JobModel, JobStatus
from app.layer6_data.models.jd.job_version_model import JobVersionModel
from app.layer6_data.models.memory_model import MemoryModel

class PostgresJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job_model: JobModel) -> JobModel:
        if not job_model.job_code:
            job_model.job_code = await self.get_next_job_code(job_model.company_id)
        
        self.session.add(job_model)
        await self.session.flush()
        return job_model

    async def save_job_version(self, version_model: JobVersionModel, archive_others: bool = True) -> JobVersionModel:
        """
        Saves a new Job Version and optionally archives previous ones.
        """
        if archive_others:
            # 1. Archive old versions for this job
            await self.session.execute(
                update(JobVersionModel)
                .where(JobVersionModel.job_id == version_model.job_id)
                .values(is_active=False)
            )
            # 2. Archive associated memories
            version_ids_query = select(JobVersionModel.id).where(JobVersionModel.job_id == version_model.job_id)
            await self.session.execute(
                update(MemoryModel)
                .where(MemoryModel.job_version_id.in_(version_ids_query))
                .values(is_active=False)
            )

        self.session.add(version_model)
        await self.session.flush()
        return version_model

    async def get_by_id(self, job_id: str) -> Optional[JobModel]:
        result = await self.session.execute(select(JobModel).filter(JobModel.id == job_id))
        return result.scalar_one_or_none()

    async def list_by_company(self, company_id: str) -> List[JobModel]:
        result = await self.session.execute(select(JobModel).filter(JobModel.company_id == company_id))
        return result.scalars().all()

    async def get_next_job_code(self, company_id: str) -> str:
        from sqlalchemy.sql import func
        count_query = select(func.count()).select_from(JobModel).where(JobModel.company_id == company_id)
        result = await self.session.execute(count_query)
        count = result.scalar() or 0
        return f"TEK-{count + 1:03d}"
