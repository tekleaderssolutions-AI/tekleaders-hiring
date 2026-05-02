from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.schemas.job_schemas import JobCreate, JobRead
from app.layer4_application.jobs.create_job import CreateJobUseCase
from app.layer6_data.repositories_impl.postgres_job_repo import PostgresJobRepository
from app.layer6_data.repositories_impl.postgres_user_repo import PostgresUserRepository
from app.layer6_data.models.company_model import CompanyModel
from app.dependencies import get_db, get_current_user
from app.layer5_domain.entities.user import User

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job posting"
)
async def create_job(
    payload: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # If the user doesn't have a company yet, create a default one for them
    company_id = current_user.company_id
    if not company_id:
        company_id = str(uuid.uuid4())
        default_company = CompanyModel(
            id=company_id,
            name=f"{current_user.first_name}'s Company",
        )
        db.add(default_company)
        
        # Update user with new company_id
        current_user.company_id = company_id
        user_repo = PostgresUserRepository(db)
        await user_repo.update(current_user)
        
        await db.commit()

    job_repo = PostgresJobRepository(db)
    use_case = CreateJobUseCase(job_repo=job_repo)
    
    try:
        job = await use_case.execute(payload, company_id=company_id, user_id=current_user.id)
        return job
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
