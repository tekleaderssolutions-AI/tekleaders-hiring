"""
Recruiter/Employee endpoints: assigned JDs, their own submission history.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies import get_db, get_current_user
from app.layer5_domain.entities.user import User
from app.layer6_data.models.jd.job_model import JobModel, JobStatus
from app.layer6_data.models.jd_assignment_model import JDAssignmentModel
from app.layer6_data.models.candidate_submission_model import CandidateSubmissionModel, SubmissionStatus
from app.layer6_data.models.client_model import ClientModel
from app.layer6_data.models.notification_model import NotificationModel
from app.layer6_data.models.interview_invitation_model import InterviewInvitationModel

router = APIRouter(prefix="/employee", tags=["Employee"])


@router.get("/dashboard")
async def employee_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = str(current_user.id)

    # Only JDs explicitly assigned to this recruiter
    assign_res = await db.execute(
        select(JDAssignmentModel).where(JDAssignmentModel.employee_id == uid)
    )
    assignments = assign_res.scalars().all()
    assigned_job_ids = {a.job_id: a for a in assignments}

    if not assigned_job_ids:
        return {
            "assigned_jds": [],
            "summary": {"total": 0, "active": 0, "pending": 0, "completed": 0},
            "my_submissions": 0,
        }

    # Fetch only those jobs
    jobs_res = await db.execute(
        select(JobModel)
        .where(JobModel.id.in_(list(assigned_job_ids.keys())))
        .order_by(JobModel.created_at.desc())
    )
    all_jobs = jobs_res.scalars().all()

    if not all_jobs:
        return {
            "assigned_jds": [],
            "summary": {"total": 0, "active": 0, "pending": 0, "completed": 0},
            "my_submissions": 0,
        }

    all_job_ids = [j.id for j in all_jobs]

    # All submissions by this recruiter (for assigned jobs only)
    sub_res = await db.execute(
        select(CandidateSubmissionModel)
        .where(CandidateSubmissionModel.submitted_by == uid)
        .where(CandidateSubmissionModel.job_id.in_(all_job_ids))
    )
    my_submissions = sub_res.scalars().all()
    subs_by_job: dict[str, int] = {}
    for s in my_submissions:
        subs_by_job[s.job_id] = subs_by_job.get(s.job_id, 0) + 1

    # Shortlisted counts (interview invitations sent by this recruiter)
    shortlisted_by_job: dict[str, int] = {}
    inv_res = await db.execute(
        select(InterviewInvitationModel.job_id, func.count(InterviewInvitationModel.id))
        .where(InterviewInvitationModel.recruiter_id == uid)
        .where(InterviewInvitationModel.job_id.in_(all_job_ids))
        .group_by(InterviewInvitationModel.job_id)
    )
    for job_id, cnt in inv_res.all():
        shortlisted_by_job[job_id] = cnt

    # Build JD cards
    jd_cards = []
    for job in all_jobs:
        client_name = None
        if job.client_id:
            cl_res = await db.execute(select(ClientModel).where(ClientModel.id == job.client_id))
            cl = cl_res.scalar_one_or_none()
            client_name = cl.name if cl else None

        assignment = assigned_job_ids.get(job.id)
        status_val = job.status.value if hasattr(job.status, "value") else (job.status or "draft")
        priority_val = job.priority.value if hasattr(job.priority, "value") else (job.priority or "medium")

        jd_cards.append({
            "job_id": job.id,
            "job_code": job.job_code,
            "title": job.current_title,
            "client_name": client_name,
            "status": status_val,
            "priority": priority_val,
            "target_count": job.target_count or 1,
            "my_submissions": subs_by_job.get(job.id, 0),
            "shortlisted": shortlisted_by_job.get(job.id, 0),
            "is_assigned": True,
            "assigned_at": assignment.assigned_at.isoformat() if assignment and assignment.assigned_at else None,
        })

    # Sort by submissions desc, then by created date
    jd_cards.sort(key=lambda j: -j["my_submissions"])

    summary = {
        "total": len(jd_cards),
        "active": sum(1 for j in jd_cards if j["status"] == "open"),
        "pending": sum(1 for j in jd_cards if j["status"] in ("draft", "on_hold")),
        "completed": sum(1 for j in jd_cards if j["status"] == "closed"),
        "assigned": len(jd_cards),
    }

    return {
        "assigned_jds": jd_cards,
        "summary": summary,
        "my_submissions": len(my_submissions),
    }


@router.get("/notifications")
async def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationModel)
        .where(NotificationModel.recipient_id == current_user.id)
        .order_by(NotificationModel.created_at.desc())
        .limit(30)
    )
    notifs = result.scalars().all()
    unread = sum(1 for n in notifs if not n.is_read)
    return {
        "unread_count": unread,
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifs
        ],
    }
