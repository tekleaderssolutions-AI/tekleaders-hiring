from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import os
import shutil
import json
from typing import List, Optional

from pydantic import BaseModel
from app.schemas.jd.job_schemas import JobCreate, JobRead
from app.layer4_application.jobs.jd.create_job import CreateJobUseCase
from app.layer4_application.jobs.jd.analyze_jd import AnalyzeJDUseCase
from app.layer6_data.repositories_impl.jd.postgres_job_repo import PostgresJobRepository
from app.layer6_data.repositories_impl.postgres_user_repo import PostgresUserRepository
from app.layer6_data.models.company_model import CompanyModel
from app.layer6_data.models.jd.job_model import JobModel
from app.dependencies import get_db, get_current_user, require_admin
from app.layer5_domain.entities.user import User
from app.config import settings

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class GenerateJDRequest(BaseModel):
    title: str
    department: str = ""
    industry: str = ""
    location: str = ""
    workplace_type: str = ""
    experience_level: str = ""
    employment_type: str = ""
    keywords: str = ""  # comma-separated skills hint


@router.post(
    "/generate-description",
    status_code=status.HTTP_200_OK,
    summary="Generate a full JD (description, requirements, benefits) from basic inputs using AI"
)
async def generate_jd_description(
    payload: GenerateJDRequest,
    current_user: User = Depends(get_current_user),
):
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    skills_hint = payload.keywords.strip()
    prompt = f"""You are an expert HR professional and technical recruiter.
Generate a comprehensive, professional job description for the following role.

Role: {payload.title}
Department: {payload.department or "Not specified"}
Industry: {payload.industry or "Not specified"}
Location: {payload.location or "Not specified"} ({payload.workplace_type or "On-site"})
Experience Level: {payload.experience_level or "Not specified"}
Employment Type: {payload.employment_type or "Full-time"}
Key Skills: {skills_hint or "To be determined based on role"}

Return ONLY a valid JSON object with exactly these three keys:
{{
  "description": "A compelling 2-3 paragraph About the Role section that excites candidates and clearly explains impact and responsibilities.",
  "requirements": "A plain-text bulleted list (use • bullet) of 8-10 must-have technical skills, qualifications, and soft skills.",
  "benefits": "A plain-text bulleted list (use • bullet) of 5-7 attractive benefits and perks."
}}

Do not include markdown, code fences, or any text outside the JSON."""

    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500,
        )
        raw = response.choices[0].message.content.strip()
        # Strip any accidental markdown code fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        return {
            "description": result.get("description", ""),
            "requirements": result.get("requirements", ""),
            "benefits": result.get("benefits", ""),
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI returned invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")

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
    use_case = CreateJobUseCase(job_repo=job_repo, db_session=db)

    try:
        job = await use_case.execute(payload, company_id=company_id, user_id=current_user.id)

        # Apply recruitment tracking fields not in the Job entity
        if payload.client_id or payload.priority or payload.target_count:
            from sqlalchemy import select as _select
            res = await db.execute(_select(JobModel).where(JobModel.id == job.id))
            job_model = res.scalar_one_or_none()
            if job_model:
                if payload.client_id:
                    job_model.client_id = payload.client_id
                if payload.priority:
                    from app.layer6_data.models.jd.job_model import JobPriority
                    try:
                        job_model.priority = JobPriority(payload.priority)
                    except ValueError:
                        pass
                if payload.target_count is not None:
                    job_model.target_count = payload.target_count
                await db.flush()

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
    summary="List jobs — admin sees all, recruiter sees only assigned"
)
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.layer6_data.models.jd_assignment_model import JDAssignmentModel
    from app.layer6_data.models.user_model import UserModel

    if not current_user.company_id:
        return []

    if current_user.role == "recruiter":
        assign_res = await db.execute(
            select(JDAssignmentModel.job_id).where(JDAssignmentModel.employee_id == current_user.id)
        )
        job_ids = [row[0] for row in assign_res.all()]
        if not job_ids:
            return []
        res = await db.execute(select(JobModel).where(JobModel.id.in_(job_ids)))
        jobs = res.scalars().all()
    else:
        job_repo = PostgresJobRepository(db)
        jobs = await job_repo.list_by_company(current_user.company_id)

    # Enrich each job with assigned employee names
    result = []
    for job in jobs:
        assign_res = await db.execute(
            select(JDAssignmentModel).where(JDAssignmentModel.job_id == job.id)
        )
        emp_ids = [a.employee_id for a in assign_res.scalars().all()]
        assigned_names = []
        if emp_ids:
            users_res = await db.execute(select(UserModel).where(UserModel.id.in_(emp_ids)))
            assigned_names = [f"{u.first_name} {u.last_name}" for u in users_res.scalars().all()]
        result.append({
            "id": job.id,
            "job_code": job.job_code,
            "current_title": job.current_title,
            "status": job.status.value if hasattr(job.status, "value") else (job.status or "draft"),
            "priority": job.priority.value if hasattr(job.priority, "value") else (job.priority or "medium"),
            "target_count": job.target_count,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "assigned_employees": assigned_names,
        })
    return result

class JobPatch(BaseModel):
    client_id: Optional[str] = None
    priority: Optional[str] = None


@router.patch(
    "/{job_id}",
    summary="Update job fields (client, priority, etc.)"
)
async def patch_job(
    job_id: str,
    payload: JobPatch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(JobModel).where(JobModel.id == job_id))
    job = res.scalar_one_or_none()
    if not job or job.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Job not found")
    if payload.client_id is not None:
        job.client_id = payload.client_id if payload.client_id else None
    if payload.priority is not None:
        from app.layer6_data.models.jd.job_model import JobPriority
        try:
            job.priority = JobPriority(payload.priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {payload.priority}")
    await db.flush()
    return {"id": job.id, "client_id": job.client_id, "priority": job.priority}


@router.get(
    "/{job_id}",
    summary="Get job details by ID"
)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.layer6_data.models.jd.job_version_model import JobVersionModel

    res = await db.execute(select(JobModel).where(JobModel.id == job_id))
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")

    jv_res = await db.execute(
        select(JobVersionModel)
        .where(JobVersionModel.job_id == job_id, JobVersionModel.is_active == True)
        .order_by(JobVersionModel.version.desc())
        .limit(1)
    )
    jv = jv_res.scalar_one_or_none()
    reqs = (jv.requirements_json or {}) if jv else {}

    return {
        "id": job.id,
        "job_code": job.job_code,
        "current_title": job.current_title,
        "status": job.status.value if hasattr(job.status, "value") else (job.status or "draft"),
        "priority": job.priority.value if hasattr(job.priority, "value") else (job.priority or "medium"),
        "description": jv.description if jv else None,
        "must_have_skills": reqs.get("must_have_skills") or reqs.get("primary_skills") or [],
        "nice_to_have_skills": reqs.get("nice_to_have_skills") or [],
        "keywords": reqs.get("keywords") or [],
        "experience_level": reqs.get("experience_level") or "",
        "experience_min": (reqs.get("experience") or {}).get("min") or 0,
        "experience_max": (reqs.get("experience") or {}).get("max") or None,
        "employment_type": reqs.get("employment_type") or "",
        "location": reqs.get("location") or "",
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }

