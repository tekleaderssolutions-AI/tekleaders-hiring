import base64
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    Credentials = None
    build = None
from pydantic import BaseModel

from app.dependencies import get_db, get_current_user
from app.config import settings
from app.layer5_domain.entities.user import User
from app.layer6_data.models.interview_invitation_model import InterviewInvitationModel

router = APIRouter(prefix="/gmail", tags=["Gmail & Calendar"])

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def _get_creds() -> Credentials:
    if not settings.GOOGLE_REFRESH_TOKEN:
        raise HTTPException(status_code=500, detail="Google refresh token not configured on server.")
    return Credentials(
        token=None,
        refresh_token=settings.GOOGLE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )


# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/status")
async def google_status():
    return {"connected": bool(settings.GOOGLE_REFRESH_TOKEN and settings.GOOGLE_SENDER_EMAIL)}


# ── Gmail ─────────────────────────────────────────────────────────────────────

class CandidateInvite(BaseModel):
    first_name: str
    last_name: str
    email: str


class JDDetails(BaseModel):
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_years: Optional[str] = None
    location: Optional[str] = None


class SendInviteRequest(BaseModel):
    job_title: str
    job_id: Optional[str] = None
    candidates: List[CandidateInvite]
    jd_details: Optional[JDDetails] = None


def _build_invite_html(
    candidate_name: str,
    job_title: str,
    jd: Optional[JDDetails],
    recruiter_name: str,
    interested_url: str,
    not_interested_url: str,
) -> str:
    # Build compact JD details block
    rows = []
    rows.append(f'<tr><td style="color:#9ca3af;padding:6px 0;width:130px;vertical-align:top;font-size:13px;">Role</td><td style="font-weight:600;font-size:13px;">{job_title}</td></tr>')
    if jd and jd.experience_years:
        rows.append(f'<tr><td style="color:#9ca3af;padding:6px 0;font-size:13px;">Experience</td><td style="font-weight:600;font-size:13px;">{jd.experience_years}</td></tr>')
    if jd and jd.location:
        rows.append(f'<tr><td style="color:#9ca3af;padding:6px 0;font-size:13px;">Work Mode</td><td style="font-weight:600;font-size:13px;">{jd.location}</td></tr>')
    if jd and jd.required_skills:
        skills_str = " · ".join(jd.required_skills[:10])
        rows.append(f'<tr><td style="color:#9ca3af;padding:6px 0;font-size:13px;vertical-align:top;">Skills</td><td style="font-weight:600;font-size:13px;">{skills_str}</td></tr>')
    if jd and jd.description:
        short = jd.description[:300] + ("…" if len(jd.description) > 300 else "")
        rows.append(f'<tr><td style="color:#9ca3af;padding:6px 0;font-size:13px;vertical-align:top;">About</td><td style="font-size:13px;color:#374151;line-height:1.6;">{short}</td></tr>')

    jd_block = f"""
    <div style="background:#f8fafc;border-radius:10px;padding:20px 24px;margin:20px 0 24px;border:1px solid #e5e7eb;">
      <table style="width:100%;border-collapse:collapse;">{''.join(rows)}</table>
    </div>""" if rows else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:560px;margin:32px auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.07);">

  <!-- Header with Tek Leaders logo -->
  <div style="background:#1a2d5a;padding:24px 36px;display:flex;align-items:center;gap:16px;">
    <div style="display:inline-flex;align-items:center;font-family:'Arial Black',Arial,sans-serif;font-size:20px;font-weight:900;">
      <span style="background:#c0001d;color:#fff;padding:3px 8px;border-radius:3px 0 0 3px;">Tek</span><span style="background:#fff;color:#1a2d5a;padding:3px 8px;border-radius:0 3px 3px 0;">Leaders</span>
    </div>
    <span style="color:#94a3b8;font-size:13px;">Recruitment Team</span>
  </div>

  <!-- Body -->
  <div style="padding:32px 36px;">
    <h2 style="font-size:19px;font-weight:700;color:#111827;margin:0 0 6px;">🎯 Your profile is a great match!</h2>
    <p style="font-size:14px;color:#374151;margin:0 0 4px;line-height:1.65;">
      Dear <b>{candidate_name}</b>,
    </p>
    <p style="font-size:14px;color:#374151;margin:0 0 4px;line-height:1.65;">
      After reviewing your profile, we believe you're an excellent fit for the opportunity below.
      We'd love to invite you for an interview.
    </p>

    {jd_block}

    <p style="font-size:14px;color:#374151;margin:0 0 20px;line-height:1.65;">
      If you're interested, click <b>Interested</b> below — we'll immediately send you
      <b>3 available interview slots</b> to choose from. The entire scheduling process is automated.
    </p>

    <!-- CTA Buttons -->
    <div style="text-align:center;margin:28px 0;">
      <a href="{interested_url}"
         style="display:inline-block;padding:13px 32px;background:#00756a;color:#fff;
                border-radius:9px;text-decoration:none;font-weight:700;font-size:15px;margin-right:10px;">
        ✅ Interested
      </a>
      <a href="{not_interested_url}"
         style="display:inline-block;padding:13px 32px;background:#fff;color:#6b7280;
                border:2px solid #e5e7eb;border-radius:9px;text-decoration:none;font-weight:700;font-size:15px;">
        ❌ Not Interested
      </a>
    </div>
  </div>

  <!-- Footer -->
  <div style="background:#f9fafb;padding:16px 36px;border-top:1px solid #f0f0f0;text-align:center;">
    <div style="font-size:11px;color:#9ca3af;">
      Sent by {recruiter_name} · Tek Leaders · recruit@tekleaders.io · Changing The Equation
    </div>
  </div>
</div>
</body>
</html>"""


@router.post("/send-invite")
async def send_interview_invite(
    payload: SendInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        creds = _get_creds()
        gmail_svc = build("gmail", "v1", credentials=creds)
        sender_name = f"{current_user.first_name} {current_user.last_name}".strip() or "Hirix Recruitment"

        base_url = "http://localhost:8000/api/v1"
        sent, failed = [], []

        for c in payload.candidates:
            try:
                name = f"{c.first_name} {c.last_name}".strip() or "Candidate"
                token = str(uuid.uuid4())

                # Persist invitation record
                inv = InterviewInvitationModel(
                    id=str(uuid.uuid4()),
                    token=token,
                    candidate_email=c.email,
                    candidate_name=name,
                    job_title=payload.job_title,
                    job_id=payload.job_id,
                    recruiter_id=str(current_user.id),
                    jd_details=payload.jd_details.model_dump_json() if payload.jd_details else None,
                    recruiter_name=sender_name,
                    company_name="Tek Leaders",
                    status="pending",
                    slot_duration_minutes=60,
                )
                db.add(inv)
                await db.flush()

                interested_url = f"{base_url}/portal/respond?token={token}&action=interested"
                not_interested_url = f"{base_url}/portal/respond?token={token}&action=not_interested"

                html_body = _build_invite_html(
                    candidate_name=name,
                    job_title=payload.job_title,
                    jd=payload.jd_details,
                    recruiter_name=sender_name,
                    interested_url=interested_url,
                    not_interested_url=not_interested_url,
                )

                msg = MIMEMultipart("alternative")
                msg["Subject"] = f"Interview Invitation — {payload.job_title} at Tek Leaders"
                msg["To"] = c.email
                msg["From"] = f"{sender_name} <{settings.GOOGLE_SENDER_EMAIL}>"
                msg.attach(MIMEText(html_body, "html"))

                raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
                gmail_svc.users().messages().send(userId="me", body={"raw": raw}).execute()
                sent.append(c.email)
            except Exception as e:
                failed.append({"email": c.email, "error": str(e)})

        return {"sent": sent, "failed": failed, "total": len(payload.candidates)}
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ── Invitation status tracking ────────────────────────────────────────────────

@router.get("/invitations")
async def list_job_invitations(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewInvitationModel)
        .where(InterviewInvitationModel.job_id == job_id)
        .where(InterviewInvitationModel.recruiter_id == str(current_user.id))
        .order_by(InterviewInvitationModel.created_at.desc())
    )
    invitations = result.scalars().all()
    return {
        "invitations": [
            {
                "id": inv.id,
                "candidate_name": inv.candidate_name,
                "candidate_email": inv.candidate_email,
                "status": inv.status,
                "meet_link": inv.meet_link,
                "selected_slot": inv.selected_slot,
                "slot_duration_minutes": inv.slot_duration_minutes,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            }
            for inv in invitations
        ]
    }


class UpdateInvStatusRequest(BaseModel):
    status: str


@router.patch("/invitations/{invitation_id}/status")
async def update_invitation_status(
    invitation_id: str,
    payload: UpdateInvStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewInvitationModel)
        .where(InterviewInvitationModel.id == invitation_id)
        .where(InterviewInvitationModel.recruiter_id == str(current_user.id))
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    allowed = {"completed", "selected", "recruiter_rejected"}
    if payload.status not in allowed:
        raise HTTPException(status_code=400, detail="Status must be one of: completed, selected, recruiter_rejected")
    inv.status = payload.status
    await db.commit()
    return {"ok": True, "status": inv.status}


# ── Mail list ─────────────────────────────────────────────────────────────────

@router.get("/messages")
async def list_messages(
    folder: str = "SENT",
    max_results: int = 30,
    current_user: User = Depends(get_current_user),
):
    try:
        creds = _get_creds()
        svc = build("gmail", "v1", credentials=creds)

        label = "SENT" if folder.upper() == "SENT" else "INBOX"
        list_res = svc.users().messages().list(
            userId="me", labelIds=[label], maxResults=max_results
        ).execute()

        messages = []
        for m in list_res.get("messages", []):
            meta = svc.users().messages().get(
                userId="me", id=m["id"],
                format="metadata",
                metadataHeaders=["Subject", "To", "From", "Date"],
            ).execute()
            headers = {h["name"]: h["value"] for h in meta.get("payload", {}).get("headers", [])}
            snippet = meta.get("snippet", "")
            messages.append({
                "id": m["id"],
                "subject": headers.get("Subject", "(No subject)"),
                "to": headers.get("To", ""),
                "from_": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": snippet,
            })

        return {"messages": messages, "total": len(messages)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{message_id}")
async def get_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
):
    creds = _get_creds()
    svc = build("gmail", "v1", credentials=creds)
    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    def extract_body(payload):
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        return ""

    return {
        "id": message_id,
        "subject": headers.get("Subject", "(No subject)"),
        "to": headers.get("To", ""),
        "from_": headers.get("From", ""),
        "date": headers.get("Date", ""),
        "body": extract_body(msg.get("payload", {})),
    }


# ── Calendar ──────────────────────────────────────────────────────────────────

@router.get("/calendar/events")
async def list_calendar_events(
    days: int = 7,
    current_user: User = Depends(get_current_user),
):
    creds = _get_creds()
    svc = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow()
    result = svc.events().list(
        calendarId="primary",
        timeMin=now.isoformat() + "Z",
        timeMax=(now + timedelta(days=days)).isoformat() + "Z",
        maxResults=50,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for e in result.get("items", []):
        start = e["start"].get("dateTime", e["start"].get("date"))
        end   = e["end"].get("dateTime",   e["end"].get("date"))
        events.append({
            "id":        e["id"],
            "title":     e.get("summary", "(No title)"),
            "start":     start,
            "end":       end,
            "meet_link": (
                e.get("conferenceData", {})
                .get("entryPoints", [{}])[0]
                .get("uri", None)
            ),
            "attendees": [a["email"] for a in e.get("attendees", [])],
            "html_link": e.get("htmlLink"),
        })

    return {"events": events, "total": len(events)}


@router.get("/calendar/busy")
async def get_busy_slots(
    date: str,
    timezone: str = "Asia/Kolkata",
    current_user: User = Depends(get_current_user),
):
    creds = _get_creds()
    svc = build("calendar", "v3", credentials=creds)

    fb = svc.freebusy().query(body={
        "timeMin": f"{date}T00:00:00Z",
        "timeMax": f"{date}T23:59:59Z",
        "timeZone": timezone,
        "items": [{"id": "primary"}],
    }).execute()

    busy = fb.get("calendars", {}).get("primary", {}).get("busy", [])
    return {"date": date, "busy": busy}
