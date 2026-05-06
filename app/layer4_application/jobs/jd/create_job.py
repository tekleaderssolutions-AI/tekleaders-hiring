from app.layer5_domain.entities.jd.job import Job
from app.layer5_domain.repositories.jd.job_repository import JobRepository
from app.schemas.jd.job_schemas import JobCreate
from datetime import datetime

class CreateJobUseCase:
    def __init__(self, job_repo: JobRepository):
        self.job_repo = job_repo

    async def execute(self, payload: JobCreate, company_id: str, user_id: str) -> Job:
        def get_val(v):
            return v.value if hasattr(v, "value") else v

        # Handle keywords (convert string to list if necessary)
        keywords_list = payload.keywords
        if isinstance(keywords_list, str):
            keywords_list = [k.strip() for k in keywords_list.split(",") if k.strip()]

        new_job = Job(
            title=payload.title,
            description=payload.description,
            employment_type=get_val(payload.employment_type),
            experience_level=get_val(payload.experience_level),
            company_id=company_id,
            created_by=user_id,
            job_code=payload.job_code,
            department=payload.department,
            workplace_type=get_val(payload.workplace_type),
            location=payload.location,
            requirements=payload.requirements,
            benefits=payload.benefits,
            industry=get_val(payload.industry) if payload.industry else None,
            job_function=get_val(payload.job_function) if payload.job_function else None,
            education_level=get_val(payload.education_level) if payload.education_level else None,
            keywords=keywords_list,
            salary_min=payload.salary_min,
            salary_max=payload.salary_max,
            salary_currency=payload.salary_currency,
            status=get_val(payload.status) if payload.status else "draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return await self.job_repo.create(new_job)
