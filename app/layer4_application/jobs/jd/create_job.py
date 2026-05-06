from app.layer5_domain.entities.jd.job import Job
from app.layer5_domain.repositories.jd.job_repository import JobRepository
from app.schemas.jd.job_schemas import JobCreate
from datetime import datetime
from app.layer2_adapters.ai.embedding_service import EmbeddingService
from app.layer6_data.models.memory_model import MemoryModel
import uuid

class CreateJobUseCase:
    def __init__(self, job_repo: JobRepository, db_session=None):
        self.job_repo = job_repo
        self.db = db_session
        self.embedder = EmbeddingService()

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
        saved_job = await self.job_repo.create(new_job)

        # ─── ELITE ADDITION: AUTO-EMBEDDING FOR SEARCH ───
        if self.db:
            # We need to find the job_version_id we just created
            # The repo creates it, so we can fetch the latest active version
            from app.layer6_data.models.jd.job_version_model import JobVersionModel
            from sqlalchemy import select
            res = await self.db.execute(
                select(JobVersionModel.id)
                .where(JobVersionModel.job_id == saved_job.id)
                .where(JobVersionModel.is_active == True)
            )
            version_id = res.scalar_one_or_none()

            if version_id:
                # Generate embeddings for the JD summary
                summary_text = f"Role: {saved_job.title}. Description: {saved_job.description}"
                vector = await self.embedder.generate_embedding(summary_text)
                
                memory = MemoryModel(
                    id=str(uuid.uuid4()),
                    job_version_id=version_id,
                    company_id=company_id,
                    cluster="other", # Default cluster
                    entity_type="job_chunk",
                    chunk_type="job_summary",
                    chunk_index=0,
                    text=summary_text,
                    embedding=vector,
                    embedding_model="text-embedding-3-small",
                    embedding_version="1.0",
                    is_active=True
                )
                self.db.add(memory)
                await self.db.flush()

        return saved_job
