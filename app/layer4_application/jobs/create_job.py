from app.layer5_domain.entities.job import Job
from app.layer5_domain.repositories.job_repository import JobRepository
from app.schemas.job_schemas import JobCreate

class CreateJobUseCase:
    def __init__(self, job_repo: JobRepository):
        self.job_repo = job_repo

    async def execute(self, payload: JobCreate, company_id: str, user_id: str) -> Job:
        new_job = Job(
            title=payload.title,
            description=payload.description,
            employment_type=payload.employment_type.value,
            experience_level=payload.experience_level.value,
            company_id=company_id,
            created_by=user_id,
            job_code=payload.job_code,
            department=payload.department,
            workplace_type=payload.workplace_type.value,
            location=payload.location,
            requirements=payload.requirements,
            benefits=payload.benefits,
            industry=payload.industry.value if payload.industry else None,
            job_function=payload.job_function.value if payload.job_function else None,
            education_level=payload.education_level.value if payload.education_level else None,
            keywords=payload.keywords,
            salary_min=payload.salary_min,
            salary_max=payload.salary_max,
            salary_currency=payload.salary_currency,
            status=payload.status.value if payload.status else "draft"
        )
        return await self.job_repo.create(new_job)
