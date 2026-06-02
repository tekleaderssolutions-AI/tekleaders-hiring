"""
Admin-only endpoints: JD assignment, JD progress tracking, employee performance, dashboard metrics.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text, update as sql_update
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uuid

from app.dependencies import get_db, get_current_user, require_admin, require_admin_or_recruiter
from app.layer5_domain.entities.user import User
from app.layer6_data.models.jd.job_model import JobModel, JobStatus
from app.layer6_data.models.jd_assignment_model import JDAssignmentModel
from app.layer6_data.models.candidate_submission_model import CandidateSubmissionModel, SubmissionStatus
from app.layer6_data.models.user_model import UserModel, UserRole
from app.layer6_data.models.client_model import ClientModel
from app.layer6_data.models.notification_model import NotificationModel, NotificationType
from app.layer6_data.repositories_impl.postgres_user_repo import PostgresUserRepository
from app.layer7_crosscutting.security import PasswordHasher

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── JD Assignment ─────────────────────────────────────────────────────────────

class AssignRequest(BaseModel):
    employee_ids: List[str]


@router.post("/jobs/{job_id}/assign")
async def assign_employees(
    job_id: str,
    payload: AssignRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    job_res = await db.execute(select(JobModel).where(JobModel.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job or job.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Job not found")

    assigned = []
    for emp_id in payload.employee_ids:
        # Verify employee exists and belongs to same company
        emp_res = await db.execute(
            select(UserModel)
            .where(UserModel.id == emp_id)
            .where(UserModel.company_id == current_user.company_id)
        )
        employee = emp_res.scalar_one_or_none()
        if not employee:
            continue

        # Check if already assigned
        existing = await db.execute(
            select(JDAssignmentModel)
            .where(JDAssignmentModel.job_id == job_id)
            .where(JDAssignmentModel.employee_id == emp_id)
        )
        if existing.scalar_one_or_none():
            assigned.append(emp_id)
            continue

        assignment = JDAssignmentModel(
            id=str(uuid.uuid4()),
            job_id=job_id,
            employee_id=emp_id,
            assigned_by=current_user.id,
        )
        db.add(assignment)
        assigned.append(emp_id)

        # Notify employee
        notif = NotificationModel(
            id=str(uuid.uuid4()),
            recipient_id=emp_id,
            company_id=current_user.company_id,
            type=NotificationType.IN_APP,
            title="New JD Assigned",
            body=f"You have been assigned to: {job.current_title or job.job_code}.",
            is_read=False,
        )
        db.add(notif)

    await db.flush()
    return {"job_id": job_id, "assigned_employee_ids": assigned}


@router.delete("/jobs/{job_id}/assign/{employee_id}")
async def unassign_employee(
    job_id: str,
    employee_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(JDAssignmentModel)
        .where(JDAssignmentModel.job_id == job_id)
        .where(JDAssignmentModel.employee_id == employee_id)
    )
    assignment = res.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await db.delete(assignment)
    await db.flush()
    return {"message": "Employee unassigned"}


# ── JD Progress ───────────────────────────────────────────────────────────────

@router.get("/jobs/{job_id}/progress")
async def get_job_progress(
    job_id: str,
    current_user: User = Depends(require_admin_or_recruiter),
    db: AsyncSession = Depends(get_db),
):
    job_res = await db.execute(select(JobModel).where(JobModel.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job or job.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Job not found")

    # Client info
    client_name = None
    if job.client_id:
        cl_res = await db.execute(select(ClientModel).where(ClientModel.id == job.client_id))
        cl = cl_res.scalar_one_or_none()
        client_name = cl.name if cl else None

    # Assigned employees
    assign_res = await db.execute(
        select(JDAssignmentModel).where(JDAssignmentModel.job_id == job_id)
    )
    assignments = assign_res.scalars().all()
    emp_ids = [a.employee_id for a in assignments]

    emp_res = await db.execute(select(UserModel).where(UserModel.id.in_(emp_ids)))
    emp_map = {u.id: u for u in emp_res.scalars().all()}

    # Submission counts
    sub_res = await db.execute(
        select(CandidateSubmissionModel)
        .where(CandidateSubmissionModel.job_id == job_id)
        .where(CandidateSubmissionModel.status == SubmissionStatus.ACTIVE)
    )
    submissions = sub_res.scalars().all()

    total_submissions = len(submissions)
    unique_emails = len({s.candidate_email for s in submissions if s.candidate_email})

    # Per-employee counts
    emp_counts = {}
    for s in submissions:
        emp_counts[s.submitted_by] = emp_counts.get(s.submitted_by, 0) + 1

    employee_stats = []
    for emp_id in emp_ids:
        emp = emp_map.get(emp_id)
        if emp:
            employee_stats.append({
                "id": emp.id,
                "name": f"{emp.first_name} {emp.last_name}",
                "email": emp.email,
                "submission_count": emp_counts.get(emp_id, 0),
            })

    return {
        "job_id": job_id,
        "job_code": job.job_code,
        "title": job.current_title,
        "client_name": client_name,
        "status": job.status,
        "priority": job.priority,
        "target_count": job.target_count,
        "total_submissions": total_submissions,
        "unique_candidates": unique_emails,
        "progress_pct": round((total_submissions / job.target_count) * 100, 1) if job.target_count else 0,
        "assigned_employees": employee_stats,
        "last_updated": job.updated_at.isoformat() if job.updated_at else None,
    }


# ── Dashboard Metrics ─────────────────────────────────────────────────────────

@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    cid = current_user.company_id
    if not cid:
        return {}

    # JD metrics
    jobs_res = await db.execute(select(JobModel).where(JobModel.company_id == cid))
    all_jobs = jobs_res.scalars().all()

    total_jds = len(all_jobs)
    active_jds = sum(1 for j in all_jobs if j.status == JobStatus.OPEN)
    closed_jds = sum(1 for j in all_jobs if j.status == JobStatus.CLOSED)
    on_hold_jds = sum(1 for j in all_jobs if j.status == JobStatus.ON_HOLD)

    # Candidate submission metrics
    sub_res = await db.execute(
        select(CandidateSubmissionModel).where(CandidateSubmissionModel.company_id == cid)
    )
    all_subs = sub_res.scalars().all()
    total_submitted = len(all_subs)
    active_subs = [s for s in all_subs if s.status == SubmissionStatus.ACTIVE]
    unique_candidates = len({s.candidate_email for s in active_subs if s.candidate_email})

    # Employee metrics
    emp_res = await db.execute(
        select(UserModel)
        .where(UserModel.company_id == cid)
        .where(UserModel.role == "recruiter")
    )
    employees = emp_res.scalars().all()

    emp_stats = []
    for emp in employees:
        emp_subs = [s for s in active_subs if s.submitted_by == emp.id]
        # Assigned JDs count
        assign_res = await db.execute(
            select(func.count(JDAssignmentModel.id))
            .where(JDAssignmentModel.employee_id == emp.id)
        )
        assigned_count = assign_res.scalar() or 0
        emp_stats.append({
            "id": emp.id,
            "name": f"{emp.first_name} {emp.last_name}",
            "email": emp.email,
            "assigned_jds": assigned_count,
            "submissions": len(emp_subs),
        })

    # Recent JDs with progress
    recent_jobs = []
    for job in sorted(all_jobs, key=lambda j: j.created_at or "", reverse=True)[:10]:
        job_subs = [s for s in active_subs if s.job_id == job.id]
        client_name = None
        if job.client_id:
            cl_res = await db.execute(select(ClientModel).where(ClientModel.id == job.client_id))
            cl = cl_res.scalar_one_or_none()
            client_name = cl.name if cl else None

        assign_res = await db.execute(
            select(JDAssignmentModel).where(JDAssignmentModel.job_id == job.id)
        )
        assigned_emp_ids = [a.employee_id for a in assign_res.scalars().all()]

        assigned_names = []
        if assigned_emp_ids:
            names_res = await db.execute(
                select(UserModel).where(UserModel.id.in_(assigned_emp_ids))
            )
            assigned_names = [f"{u.first_name} {u.last_name}" for u in names_res.scalars().all()]

        recent_jobs.append({
            "id": job.id,
            "job_code": job.job_code,
            "title": job.current_title,
            "client_id": job.client_id,
            "client_name": client_name,
            "status": job.status,
            "priority": job.priority,
            "target_count": job.target_count,
            "submissions": len(job_subs),
            "assigned_count": len(assigned_emp_ids),
            "assigned_employees": assigned_names,
            "last_updated": job.updated_at.isoformat() if job.updated_at else None,
        })

    return {
        "jd_metrics": {
            "total": total_jds,
            "active": active_jds,
            "closed": closed_jds,
            "on_hold": on_hold_jds,
        },
        "candidate_metrics": {
            "total_submitted": total_submitted,
            "unique_candidates": unique_candidates,
        },
        "employee_metrics": emp_stats,
        "recent_jobs": recent_jobs,
    }


# ── Employee Performance ──────────────────────────────────────────────────────

@router.get("/employees/{employee_id}/performance")
async def employee_performance(
    employee_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    emp_res = await db.execute(
        select(UserModel)
        .where(UserModel.id == employee_id)
        .where(UserModel.company_id == current_user.company_id)
    )
    emp = emp_res.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Assigned JDs
    assign_res = await db.execute(
        select(JDAssignmentModel).where(JDAssignmentModel.employee_id == employee_id)
    )
    assignments = assign_res.scalars().all()
    job_ids = [a.job_id for a in assignments]

    # Submissions by this employee
    sub_res = await db.execute(
        select(CandidateSubmissionModel)
        .where(CandidateSubmissionModel.submitted_by == employee_id)
        .order_by(CandidateSubmissionModel.submitted_at.desc())
    )
    submissions = sub_res.scalars().all()

    active_subs = [s for s in submissions if s.status == SubmissionStatus.ACTIVE]

    return {
        "employee": {
            "id": emp.id,
            "name": f"{emp.first_name} {emp.last_name}",
            "email": emp.email,
        },
        "assigned_jd_count": len(job_ids),
        "total_submissions": len(submissions),
        "active_submissions": len(active_subs),
        "submissions": [
            {
                "id": s.id,
                "job_id": s.job_id,
                "candidate_name": s.candidate_name,
                "candidate_email": s.candidate_email,
                "ranking": s.ranking.value if s.ranking else None,
                "status": s.status.value,
                "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
            }
            for s in active_subs
        ],
    }


# ── Update JD Status ──────────────────────────────────────────────────────────

class JobStatusUpdate(BaseModel):
    status: str


@router.patch("/jobs/{job_id}/status")
async def update_job_status(
    job_id: str,
    payload: JobStatusUpdate,
    current_user: User = Depends(require_admin_or_recruiter),
    db: AsyncSession = Depends(get_db),
):
    job_res = await db.execute(select(JobModel).where(JobModel.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job or job.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Job not found")

    valid_statuses = {s.value for s in JobStatus}
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{payload.status}'. Must be one of: {sorted(valid_statuses)}")

    try:
        # Use raw SQL to avoid PostgreSQL native-enum type mismatches on existing tables
        await db.execute(
            text("UPDATE jobs SET status = :status WHERE id = :job_id"),
            {"status": payload.status, "job_id": job_id},
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DB error updating status: {str(e)}")

    # Notify assigned employees about status change
    assign_res = await db.execute(
        select(JDAssignmentModel).where(JDAssignmentModel.job_id == job_id)
    )
    for assignment in assign_res.scalars().all():
        notif = NotificationModel(
            id=str(uuid.uuid4()),
            recipient_id=assignment.employee_id,
            company_id=current_user.company_id,
            type=NotificationType.IN_APP,
            title="JD Status Updated",
            body=f"The JD '{job.current_title or job.job_code}' is now {payload.status.upper()}.",
            is_read=False,
        )
        db.add(notif)

    await db.flush()
    return {"job_id": job_id, "status": payload.status}


# ── Employee Management ───────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "recruiter"


class EmployeeUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/employees")
async def list_employees(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(UserModel).order_by(UserModel.created_at.desc())
    if current_user.company_id:
        query = query.where(UserModel.company_id == current_user.company_id)
    else:
        return []
    res = await db.execute(query)
    employees = res.scalars().all()
    return [
        {
            "id": e.id,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "name": f"{e.first_name} {e.last_name}",
            "email": e.email,
            "role": e.role.value if hasattr(e.role, "value") else e.role,
            "is_active": e.is_active,
            "is_current_user": e.id == current_user.id,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in employees
    ]


@router.post("/employees", status_code=201)
async def create_employee(
    payload: EmployeeCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    repo = PostgresUserRepository(db)
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    valid_roles = {r.value for r in UserRole}
    role = payload.role if payload.role in valid_roles else "recruiter"

    from app.layer5_domain.entities.user import User as UserEntity
    new_user = UserEntity(
        id=None,
        email=payload.email,
        hashed_password=PasswordHasher.hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_id=current_user.company_id,
        role=role,
    )
    created = await repo.create(new_user)
    return {
        "id": created.id,
        "name": f"{created.first_name} {created.last_name}",
        "email": created.email,
        "role": role,
        "is_active": True,
    }


@router.patch("/employees/{employee_id}")
async def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(UserModel)
        .where(UserModel.id == employee_id)
        .where(UserModel.company_id == current_user.company_id)
    )
    emp = res.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    if payload.role is not None:
        try:
            emp.role = UserRole(payload.role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {payload.role}")

    if payload.is_active is not None:
        emp.is_active = payload.is_active

    await db.flush()
    return {
        "id": emp.id,
        "name": f"{emp.first_name} {emp.last_name}",
        "email": emp.email,
        "role": emp.role.value if hasattr(emp.role, "value") else emp.role,
        "is_active": emp.is_active,
    }


class ResetPasswordPayload(BaseModel):
    new_password: str


@router.post("/employees/{employee_id}/reset-password", status_code=200)
async def reset_employee_password(
    employee_id: str,
    payload: ResetPasswordPayload,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    res = await db.execute(
        select(UserModel)
        .where(UserModel.id == employee_id)
        .where(UserModel.company_id == current_user.company_id)
    )
    emp = res.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp.hashed_password = PasswordHasher.hash(payload.new_password)
    await db.flush()
    return {"message": f"Password reset for {emp.first_name} {emp.last_name}"}


# ── Notifications ─────────────────────────────────────────────────────────────

@router.get("/notifications")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationModel)
        .where(NotificationModel.recipient_id == current_user.id)
        .order_by(NotificationModel.created_at.desc())
        .limit(50)
    )
    notifs = result.scalars().all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "body": n.body,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifs
    ]


@router.patch("/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(NotificationModel)
        .where(NotificationModel.id == notif_id)
        .where(NotificationModel.recipient_id == current_user.id)
    )
    notif = res.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.flush()
    return {"id": notif_id, "is_read": True}
