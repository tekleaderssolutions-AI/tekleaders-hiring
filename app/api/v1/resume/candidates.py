from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid

from app.database import AsyncSessionLocal
from app.dependencies import get_db, get_current_user
from app.layer4_application.resume.parse_resume import ParseResumeUseCase
from app.layer5_domain.entities.user import User
from app.layer6_data.repositories_impl.resume.postgres_candidate_repo import PostgresCandidateRepository

router = APIRouter(prefix="/candidates", tags=["Candidates"])


async def _create_submission_from_resume(db, resume_id: str, job_id: str, user_id: str, company_id: str):
    """Create a CandidateSubmissionModel after a resume is parsed, if not already submitted."""
    from app.layer6_data.models.resume.resume_model import ResumeModel
    from app.layer6_data.models.resume.candidate_model import CandidateModel
    from app.layer6_data.models.candidate_submission_model import CandidateSubmissionModel, SubmissionStatus

    res = await db.execute(select(ResumeModel).where(ResumeModel.id == resume_id))
    resume = res.scalar_one_or_none()
    if not resume:
        return

    cand_res = await db.execute(select(CandidateModel).where(CandidateModel.id == resume.candidate_id))
    candidate = cand_res.scalar_one_or_none()
    if not candidate:
        return

    # Skip if already submitted for this job
    existing = await db.execute(
        select(CandidateSubmissionModel)
        .where(CandidateSubmissionModel.job_id == job_id)
        .where(CandidateSubmissionModel.candidate_email == candidate.email)
        .where(CandidateSubmissionModel.status != SubmissionStatus.WITHDRAWN)
    )
    if existing.scalar_one_or_none():
        return

    metadata = resume.metadata_json or {}
    seniority = metadata.get("seniority", {})
    experience_years = seniority.get("total_years") or seniority.get("total_experience_years")

    submission = CandidateSubmissionModel(
        id=str(uuid.uuid4()),
        job_id=job_id,
        candidate_id=resume.candidate_id,
        resume_id=resume_id,
        submitted_by=user_id,
        company_id=company_id,
        candidate_name=f"{candidate.first_name or ''} {candidate.last_name or ''}".strip() or None,
        candidate_email=candidate.email,
        candidate_phone=candidate.phone,
        experience_years=float(experience_years) if experience_years else None,
        skills=resume.skills_json or [],
        status=SubmissionStatus.ACTIVE,
    )
    db.add(submission)
    await db.flush()


async def process_bulk_resumes(content: bytes, user_id: str, session_id: str = None, job_id: str = None, company_id: str = None):
    """Background task: parallel resume processing with per-file progress updates."""
    from app.database import AsyncSessionLocal
    from app.layer6_data.models.resume.bulk_upload_model import BulkUploadModel
    from sqlalchemy import update

    # execute_bulk manages its own per-file sessions and increments processed_count live
    use_case = ParseResumeUseCase(None)
    results = await use_case.execute_bulk(content, user_id, session_id=session_id)

    # Auto-create submissions for all successfully parsed resumes
    if job_id and company_id:
        async with AsyncSessionLocal() as db:
            for r in results:
                if r.get("status") == "success" and r.get("id"):
                    try:
                        await _create_submission_from_resume(db, r["id"], job_id, user_id, company_id)
                    except Exception as e:
                        print(f"[bulk submission] skipping {r.get('id')}: {e}")
            await db.commit()

    # Mark session completed once all files are done
    if session_id:
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(BulkUploadModel)
                .where(BulkUploadModel.id == session_id)
                .values(status="completed")
            )
            await db.commit()

@router.post(
    "/upload",
    summary="Smart Upload: Handles single PDF/DOCX or Bulk ZIP files"
)
async def upload_resumes(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    use_case = ParseResumeUseCase(db)
    content = await file.read()
    filename = file.filename.lower()

    # 1. Check if it's a Bulk ZIP -> Run in Background
    if filename.endswith(".zip"):
        import zipfile
        import io
        import hashlib
        from app.layer6_data.models.resume.bulk_upload_model import BulkUploadModel

        with zipfile.ZipFile(io.BytesIO(content)) as z:
            filenames = [f for f in z.namelist() if f.lower().endswith(('.pdf', '.docx')) and not f.startswith('__MACOSX')]
            total_count = len(filenames)

            # Pre-scan for duplicates
            seen_hashes = set()
            unique_count = 0
            duplicate_count = 0
            for fname in filenames:
                with z.open(fname) as f:
                    f_hash = hashlib.md5(f.read()).hexdigest()
                    if f_hash in seen_hashes:
                        duplicate_count += 1
                    else:
                        seen_hashes.add(f_hash)
                        unique_count += 1

        # Create Tracking Session
        session_id = f"bulk_{str(uuid.uuid4())[:8]}"
        async with AsyncSessionLocal() as session:
            tracking = BulkUploadModel(
                id=session_id,
                user_id=current_user.id,
                total_files=total_count,
                unique_files=unique_count,
                duplicate_files=duplicate_count,
                status="processing"
            )
            session.add(tracking)
            await session.commit()

        background_tasks.add_task(
            process_bulk_resumes, content, current_user.id, session_id,
            job_id, current_user.company_id
        )
        return {
            "mode": "bulk",
            "session_id": session_id,
            "total_files": total_count,
            "unique_files": unique_count,
            "duplicate_files": duplicate_count,
            "message": f"Processing {unique_count} unique resumes. {duplicate_count} duplicates skipped."
        }

    # 2. Otherwise process as a Single File
    result = await use_case.execute_single(content, file.filename, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Auto-create submission record so dashboard counts update immediately.
    # Use a fresh session — execute_single already committed the request session mid-way,
    # which leaves get_db's managed transaction in an invalid state for further writes.
    if job_id and result.get("resume_id"):
        try:
            async with AsyncSessionLocal() as sub_db:
                await _create_submission_from_resume(
                    sub_db, result["resume_id"], job_id, current_user.id, current_user.company_id
                )
                await sub_db.commit()
        except Exception as e:
            print(f"[submission] failed to create submission: {e}")

    return {
        "mode": "single",
        "data": result
    }

def _compute_experience_years(work_experience: list) -> float | None:
    """Sum duration of all work experience entries from their start/end dates."""
    from datetime import datetime
    if not work_experience:
        return None

    MONTH_MAP = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    def parse_date(s):
        if not s:
            return None
        s = str(s).strip().lower()
        if s in ('present', 'current', 'now', 'till date', 'till now', 'ongoing'):
            return datetime.now()
        parts = s.split()
        if len(parts) == 2:
            month = MONTH_MAP.get(parts[0][:3])
            try:
                year = int(parts[1])
                if month:
                    return datetime(year, month, 1)
            except ValueError:
                pass
        try:
            return datetime(int(s), 6, 1)  # year-only → mid-year estimate
        except ValueError:
            return None

    total_months = 0
    for job in work_experience:
        start = parse_date(job.get("start_date") or job.get("start"))
        end = parse_date(job.get("end_date") or job.get("end") or "Present")
        if start and end and end >= start:
            total_months += (end.year - start.year) * 12 + (end.month - start.month)

    return round(total_months / 12, 1) if total_months > 0 else None


@router.get(
    "",
    summary="List all candidates with uploader info"
)
async def list_candidates(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import select, func, and_
    from app.layer6_data.models.resume.candidate_model import CandidateModel
    from app.layer6_data.models.resume.resume_model import ResumeModel
    from app.layer6_data.models.user_model import UserModel

    # Subquery: latest resume created_at per candidate
    latest_sq = (
        select(ResumeModel.candidate_id, func.max(ResumeModel.created_at).label("max_at"))
        .group_by(ResumeModel.candidate_id)
        .subquery()
    )

    stmt = (
        select(
            CandidateModel.id,
            CandidateModel.email,
            CandidateModel.first_name,
            CandidateModel.last_name,
            CandidateModel.phone,
            CandidateModel.created_at,
            ResumeModel.id.label("resume_id"),
            ResumeModel.title.label("resume_title"),
            ResumeModel.skills_json,
            ResumeModel.experience_json,
            ResumeModel.metadata_json,
            ResumeModel.uploaded_by,
            (UserModel.first_name + " " + UserModel.last_name).label("added_by_name"),
        )
        .join(latest_sq, latest_sq.c.candidate_id == CandidateModel.id)
        .join(
            ResumeModel,
            and_(
                ResumeModel.candidate_id == CandidateModel.id,
                ResumeModel.created_at == latest_sq.c.max_at,
            ),
        )
        .outerjoin(UserModel, UserModel.id == ResumeModel.uploaded_by)
        .where(
            ResumeModel.uploaded_by == current_user.id
            if current_user.role == "recruiter"
            else ResumeModel.uploaded_by.in_(
                select(UserModel.id).where(UserModel.company_id == current_user.company_id)
            )
        )
        .order_by(CandidateModel.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    rows = result.all()

    # Batch-fetch jobs each candidate was submitted to
    from app.layer6_data.models.candidate_submission_model import CandidateSubmissionModel
    from app.layer6_data.models.jd.job_model import JobModel

    candidate_ids = [r.id for r in rows]
    jobs_map: dict[str, list] = {cid: [] for cid in candidate_ids}

    if candidate_ids:
        sub_stmt = (
            select(
                CandidateSubmissionModel.candidate_id,
                JobModel.id.label("job_id"),
                JobModel.current_title,
                JobModel.job_code,
            )
            .join(JobModel, JobModel.id == CandidateSubmissionModel.job_id)
            .where(CandidateSubmissionModel.candidate_id.in_(candidate_ids))
            .distinct()
        )
        sub_result = await db.execute(sub_stmt)
        for s in sub_result.all():
            if s.candidate_id in jobs_map:
                jobs_map[s.candidate_id].append({
                    "job_id": s.job_id,
                    "title": s.current_title or s.job_code or "Untitled",
                    "job_code": s.job_code,
                })

    return [
        {
            "id": r.id,
            "resume_id": r.resume_id,
            "name": f"{r.first_name or ''} {r.last_name or ''}".strip() or "Unknown",
            "email": r.email,
            "phone": r.phone,
            "resume_title": r.resume_title,
            "skills": r.skills_json or [],
            "experience_years": (
                _compute_experience_years(r.experience_json)
                or (r.metadata_json or {}).get("seniority", {}).get("total_years")
            ),
            "added_by": r.added_by_name or "Unknown",
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "jobs": jobs_map.get(r.id, []),
        }
        for r in rows
    ]

@router.get(
    "/progress/{session_id}",
    summary="Get lively progress for a bulk upload session"
)
async def get_bulk_progress(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.layer6_data.models.resume.bulk_upload_model import BulkUploadModel
    from sqlalchemy.future import select
    
    result = await db.execute(
        select(BulkUploadModel).where(BulkUploadModel.id == session_id)
    )
    tracking = result.scalar_one_or_none()
    
    if not tracking:
        raise HTTPException(status_code=404, detail="Bulk session not found")
        
    return {
        "session_id": tracking.id,
        "total": tracking.total_files,
        "unique": tracking.unique_files,
        "duplicates": tracking.duplicate_files,
        "processed": tracking.processed_count,
        "status": tracking.status
    }

@router.get(
    "/stats",
    summary="Get candidate processing stats"
)
async def get_candidate_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PostgresCandidateRepository(db)
    count = await repo.count_candidates() # I will add this method to the repo
    return {"total_count": count}

@router.get(
    "/{candidate_id}",
    summary="Get candidate details by ID"
)
async def get_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PostgresCandidateRepository(db)
    candidate = await repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
