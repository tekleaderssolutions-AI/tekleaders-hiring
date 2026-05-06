from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, update
import uuid

from app.layer6_data.models.jd.job_model import JobModel, JobStatus
from app.layer6_data.models.jd.job_version_model import JobVersionModel
from app.layer6_data.models.memory_model import MemoryModel
from app.layer5_domain.entities.jd.job import Job

class PostgresJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job: Job) -> Job:
        """
        Implementation of the JobRepository interface.
        Maps the Job domain entity to the JobModel and JobVersionModel.
        """
        job_id = str(uuid.uuid4())
        
        # 1. Create the base Job Identity
        if not job.job_code:
            job.job_code = await self.get_next_job_code(job.company_id)
            
        job_model = JobModel(
            id=job_id,
            company_id=job.company_id,
            created_by=job.created_by,
            job_code=job.job_code,
            current_title=job.title,
            status=job.status
        )
        self.session.add(job_model)
        
        # 2. Create the first Job Version (snapshot of the requirements)
        version_id = str(uuid.uuid4())
        version_model = JobVersionModel(
            id=version_id,
            job_id=job_id,
            title=job.title,
            description=job.description,
            requirements_json={
                "requirements": job.requirements,
                "benefits": job.benefits,
                "industry": job.industry,
                "job_function": job.job_function,
                "experience_level": job.experience_level,
                "employment_type": job.employment_type,
                "education_level": job.education_level,
                "location": job.location,
                "workplace_type": job.workplace_type,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_currency": job.salary_currency,
                "keywords": job.keywords
            },
            version=1,
            is_active=True
        )
        self.session.add(version_model)
        
        await self.session.flush()
        
        job.id = job_id
        return job

    async def save_job_version(self, version_model: JobVersionModel, archive_others: bool = True) -> JobVersionModel:
        if archive_others:
            await self.session.execute(
                update(JobVersionModel)
                .where(JobVersionModel.job_id == version_model.job_id)
                .values(is_active=False)
            )
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
