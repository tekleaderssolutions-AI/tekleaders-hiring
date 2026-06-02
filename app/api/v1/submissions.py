from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
import uuid

from app.dependencies import get_db, get_current_user, require_admin
from app.layer5_domain.entities.user import User
from app.layer6_data.models.candidate_submission_model import CandidateSubmissionModel, SubmissionStatus
from app.layer6_data.models.jd_assignment_model import JDAssignmentModel
from app.layer6_data.models.jd.job_model import JobModel
from app.layer6_data.models.notification_model import NotificationModel

router = APIRouter(prefix="/submissions", tags=["Candidate Submissions"])


class SubmissionCreate(BaseModel):
    job_id: str
    candidate_name: str
    candidate_email: str
    candidate_phone: Optional[str] = None
    candidate_linkedin: Optional[str] = None
    experience_years: Optional[float] = None
    current_company: Optional[str] = None
    current_location: Optional[str] = None
    notice_period: Optional[str] = None
    skills: Optional[List[str]] = None
    ranking: Optional[str] = None
    notes: Optional[str] = None


class RankingUpdate(BaseModel):
    ranking: str


class SubmissionRead(BaseModel):
    id: str
    job_id: str
    candidate_name: Optional[str]
    candidate_email: Optional[str]
    candidate_phone: Optional[str]
    candidate_linkedin: Optional[str]
    experience_years: Optional[float]
    current_company: Optional[str]
    current_location: Optional[str]
    notice_period: Optional[str]
    skills: Optional[List[str]]
    ranking: Optional[str]
    notes: Optional[str]
    status: str
    submitted_by_name: Optional[str] = None
    submitted_at: Optional[str] = None
    duplicate_of: Optional[str] = None

    class Config:
        from_attributes = True


async def _notify(db: AsyncSession, user_id: str, company_id: str, title: str, body: str):
    from app.layer6_data.models.notification_model import NotificationType
    notif = NotificationModel(
        id=str(uuid.uuid4()),
        recipient_id=user_id,
        company_id=company_id,
        type=NotificationType.IN_APP,
        title=title,
        body=body,
        is_read=False,
    )
    db.add(notif)


@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_candidate(
    payload: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify job exists and belongs to user's company
    job_res = await db.execute(select(JobModel).where(JobModel.id == payload.job_id))
    job = job_res.scalar_one_or_none()
    if not job or job.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Job not found")

    # Employees can only submit to assigned JDs
    if current_user.role == "recruiter":
        assign_res = await db.execute(
            select(JDAssignmentModel)
            .where(JDAssignmentModel.job_id == payload.job_id)
            .where(JDAssignmentModel.employee_id == current_user.id)
        )
        if not assign_res.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="You are not assigned to this JD")

    # Duplicate detection: email first, then phone, then linkedin
    existing_by_email = None
    if payload.candidate_email:
        res = await db.execute(
            select(CandidateSubmissionModel)
            .where(CandidateSubmissionModel.job_id == payload.job_id)
            .where(CandidateSubmissionModel.candidate_email == payload.candidate_email.lower().strip())
            .where(CandidateSubmissionModel.status != SubmissionStatus.WITHDRAWN)
        )
        existing_by_email = res.scalar_one_or_none()

    if existing_by_email:
        # Fetch name of original submitter for the error message
        from app.layer6_data.models.user_model import UserModel
        sub_res = await db.execute(select(UserModel).where(UserModel.id == existing_by_email.submitted_by))
        orig_submitter = sub_res.scalar_one_or_none()
        orig_name = f"{orig_submitter.first_name} {orig_submitter.last_name}" if orig_submitter else "another recruiter"
        orig_date = existing_by_email.submitted_at.strftime("%d %b %Y %H:%M") if existing_by_email.submitted_at else "earlier"
        raise HTTPException(
            status_code=409,
            detail=f"Candidate already submitted by {orig_name} on {orig_date}."
        )

    submission = CandidateSubmissionModel(
        id=str(uuid.uuid4()),
        job_id=payload.job_id,
        submitted_by=current_user.id,
        company_id=current_user.company_id,
        candidate_name=payload.candidate_name,
        candidate_email=payload.candidate_email.lower().strip() if payload.candidate_email else None,
        candidate_phone=payload.candidate_phone,
        candidate_linkedin=payload.candidate_linkedin,
        experience_years=payload.experience_years,
        current_company=payload.current_company,
        current_location=payload.current_location,
        notice_period=payload.notice_period,
        skills=payload.skills,
        ranking=payload.ranking,
        notes=payload.notes,
        status=SubmissionStatus.ACTIVE,
    )
    db.add(submission)
    await db.flush()

    # Notify admin: candidate submitted
    from app.layer6_data.models.user_model import UserModel
    admin_res = await db.execute(
        select(UserModel)
        .where(UserModel.company_id == current_user.company_id)
        .where(UserModel.role == "admin")
    )
    for admin in admin_res.scalars().all():
        await _notify(
            db, admin.id, current_user.company_id,
            "New Candidate Submitted",
            f"{current_user.first_name} {current_user.last_name} submitted {payload.candidate_name} for {job.current_title or job.job_code}."
        )

    return {"id": submission.id, "status": "active", "message": "Candidate submitted successfully"}


@router.get("/job/{job_id}", response_model=List[SubmissionRead])
async def list_submissions_for_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = (current_user.role or "").lower().strip()

    # Non-admins must be assigned to the JD
    if role != "admin":
        assign_res = await db.execute(
            select(JDAssignmentModel)
            .where(JDAssignmentModel.job_id == job_id)
            .where(JDAssignmentModel.employee_id == current_user.id)
        )
        if not assign_res.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="You are not assigned to this JD")

    query = (
        select(CandidateSubmissionModel)
        .where(CandidateSubmissionModel.job_id == job_id)
        .where(CandidateSubmissionModel.company_id == current_user.company_id)
    )

    # Non-admins only see resumes they uploaded themselves
    if role != "admin":
        query = query.where(CandidateSubmissionModel.submitted_by == current_user.id)

    query = query.order_by(CandidateSubmissionModel.submitted_at.desc())
    result = await db.execute(query)
    submissions = result.scalars().all()

    from app.layer6_data.models.user_model import UserModel
    user_ids = list({s.submitted_by for s in submissions})
    user_res = await db.execute(select(UserModel).where(UserModel.id.in_(user_ids)))
    users = {u.id: f"{u.first_name} {u.last_name}" for u in user_res.scalars().all()}

    return [
        SubmissionRead(
            id=s.id, job_id=s.job_id,
            candidate_name=s.candidate_name, candidate_email=s.candidate_email,
            candidate_phone=s.candidate_phone, candidate_linkedin=s.candidate_linkedin,
            experience_years=s.experience_years, current_company=s.current_company,
            current_location=s.current_location, notice_period=s.notice_period,
            skills=s.skills, ranking=s.ranking.value if s.ranking else None,
            notes=s.notes, status=s.status.value,
            submitted_by_name=users.get(s.submitted_by),
            submitted_at=s.submitted_at.isoformat() if s.submitted_at else None,
            duplicate_of=s.duplicate_of,
        )
        for s in submissions
    ]


@router.patch("/{submission_id}/ranking")
async def update_ranking(
    submission_id: str,
    payload: RankingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CandidateSubmissionModel).where(CandidateSubmissionModel.id == submission_id)
    )
    sub = result.scalar_one_or_none()
    if not sub or sub.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Submission not found")
    if current_user.role == "recruiter" and sub.submitted_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own submissions")

    sub.ranking = payload.ranking
    await db.flush()
    return {"id": sub.id, "ranking": payload.ranking}


@router.delete("/{submission_id}")
async def withdraw_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CandidateSubmissionModel).where(CandidateSubmissionModel.id == submission_id)
    )
    sub = result.scalar_one_or_none()
    if not sub or sub.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Submission not found")
    if current_user.role == "recruiter" and sub.submitted_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    sub.status = SubmissionStatus.WITHDRAWN
    await db.flush()
    return {"message": "Submission withdrawn"}
