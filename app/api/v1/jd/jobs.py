from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import os
import shutil
from typing import List

from app.schemas.jd.job_schemas import JobCreate, JobRead
from app.layer4_application.jobs.jd.create_job import CreateJobUseCase
from app.layer4_application.jobs.jd.analyze_jd import AnalyzeJDUseCase
from app.layer6_data.repositories_impl.jd.postgres_job_repo import PostgresJobRepository
from app.layer6_data.repositories_impl.postgres_user_repo import PostgresUserRepository
from app.layer6_data.models.company_model import CompanyModel
from app.dependencies import get_db, get_current_user
from app.layer5_domain.entities.user import User

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
    summary="Upload and analyze a JD (PDF/DOCX) using AI"
)
async def analyze_jd(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Create temp directory if it doesn't exist
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
    
    try:
        # Save file locally for processing
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        use_case = AnalyzeJDUseCase(db)
        result = await use_case.execute(file_path, user_id=current_user.id)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job posting manually"
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
        # Transactions are managed by get_db dependency (session.begin())

    job_repo = PostgresJobRepository(db)
    use_case = CreateJobUseCase(job_repo=job_repo)
    
    try:
        job = await use_case.execute(payload, company_id=company_id, user_id=current_user.id)
        return job
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/next-code",
    summary="Get the next sequential Job Code (TEK-XXX) for the company"
)
async def get_next_job_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.company_id:
        return {"next_code": "TEK-001"}
    
    job_repo = PostgresJobRepository(db)
    next_code = await job_repo.get_next_job_code(current_user.company_id)
    return {"next_code": next_code}

@router.get(
    "",
    summary="List all jobs for the current company"
)
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.company_id:
        return []
        
    job_repo = PostgresJobRepository(db)
    jobs = await job_repo.list_by_company(current_user.company_id)
    return jobs

@router.get(
    "/{job_id}",
    summary="Get job details by ID"
)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job_repo = PostgresJobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Optional: Verify user has access to this job's company
    if job.company_id != current_user.company_id:
         raise HTTPException(status_code=403, detail="Not authorized to view this job")
         
    return job

