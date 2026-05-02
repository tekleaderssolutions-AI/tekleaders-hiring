from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.layer5_domain.entities.job import Job
from app.layer5_domain.repositories.job_repository import JobRepository
from app.layer6_data.models.job_model import JobModel

class PostgresJobRepository(JobRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: JobModel) -> Job:
        def get_val(v):
            return v.value if hasattr(v, "value") else v

        return Job(
            id=model.id,
            title=model.title,
            description=model.description,
            employment_type=get_val(model.employment_type) if model.employment_type else None,
            experience_level=get_val(model.experience_level) if model.experience_level else None,
            company_id=model.company_id,
            created_by=model.created_by,
            job_code=model.job_code,
            department=model.department,
            workplace_type=get_val(model.workplace_type) if model.workplace_type else None,
            location=model.location,
            requirements=model.requirements,
            benefits=model.benefits,
            industry=get_val(model.industry) if model.industry else None,
            job_function=get_val(model.job_function) if model.job_function else None,
            education_level=get_val(model.education_level) if model.education_level else None,
            keywords=model.keywords,
            salary_min=model.salary_min,
            salary_max=model.salary_max,
            salary_currency=model.salary_currency,
            status=get_val(model.status) if model.status else None,
            published_at=model.published_at,
            closed_at=model.closed_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: Job) -> JobModel:
        return JobModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            employment_type=entity.employment_type,
            experience_level=entity.experience_level,
            company_id=entity.company_id,
            created_by=entity.created_by,
            job_code=entity.job_code,
            department=entity.department,
            workplace_type=entity.workplace_type,
            location=entity.location,
            requirements=entity.requirements,
            benefits=entity.benefits,
            industry=entity.industry,
            job_function=entity.job_function,
            education_level=entity.education_level,
            keywords=entity.keywords,
            salary_min=entity.salary_min,
            salary_max=entity.salary_max,
            salary_currency=entity.salary_currency,
            status=entity.status
        )

    async def create(self, job: Job) -> Job:
        if not job.job_code:
            job.job_code = await self.get_next_job_code(job.company_id)

        db_job = self._to_model(job)
        self.session.add(db_job)
        await self.session.flush()
        return self._to_entity(db_job)

    async def get_by_id(self, job_id: str) -> Optional[Job]:
        result = await self.session.execute(select(JobModel).filter(JobModel.id == job_id))
        model = result.scalar_one_or_none()
        if model:
            return self._to_entity(model)
        return None

    async def list_by_company(self, company_id: str) -> List[Job]:
        result = await self.session.execute(select(JobModel).filter(JobModel.company_id == company_id))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, job: Job) -> Job:
        db_job = await self.session.execute(select(JobModel).filter(JobModel.id == job.id))
        db_job = db_job.scalar_one_or_none()
        if db_job:
            db_job.title = job.title
            db_job.description = job.description
            db_job.employment_type = job.employment_type
            db_job.experience_level = job.experience_level
            db_job.job_code = job.job_code
            db_job.department = job.department
            db_job.workplace_type = job.workplace_type
            db_job.location = job.location
            db_job.requirements = job.requirements
            db_job.benefits = job.benefits
            db_job.industry = job.industry
            db_job.job_function = job.job_function
            db_job.education_level = job.education_level
            db_job.keywords = job.keywords
            db_job.salary_min = job.salary_min
            db_job.salary_max = job.salary_max
            db_job.salary_currency = job.salary_currency
            db_job.status = job.status
            
            await self.session.flush()
            return self._to_entity(db_job)
        raise ValueError("Job not found")

    async def get_next_job_code(self, company_id: str) -> str:
        from sqlalchemy.sql import func
        count_query = select(func.count()).select_from(JobModel).where(JobModel.company_id == company_id)
        result = await self.session.execute(count_query)
        count = result.scalar() or 0
        return f"TEK-{count + 1:03d}"

