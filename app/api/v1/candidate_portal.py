"""
Public candidate-facing endpoints — no auth required.
Candidates click links in emails; these pages handle their responses.
"""
import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.dependencies import get_db
from app.config import settings
from app.layer6_data.models.interview_invitation_model import InterviewInvitationModel

router = APIRouter(prefix="/portal", tags=["Candidate Portal"])

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]

IST_OFFSET    = timedelta(hours=5, minutes=30)
BUSINESS_START = 9
BUSINESS_END   = 18

TEK_LOGO_HTML = """
<div style="display:inline-flex;align-items:center;gap:0;font-family:'Arial Black',Arial,sans-serif;font-size:22px;font-weight:900;letter-spacing:-0.5px;">
  <span style="background:#c0001d;color:#fff;padding:4px 10px 4px 10px;border-radius:4px 0 0 4px;">Tek</span><span style="background:#1a2d5a;color:#fff;padding:4px 10px 4px 8px;border-radius:0 4px 4px 0;">Leaders</span>
</div>
<div style="font-size:9px;color:#9ca3af;letter-spacing:.12em;text-transform:uppercase;margin-top:4px;">Changing The Equation</div>
"""


def _get_creds() -> Credentials:
    return Credentials(
        token=None,
        refresh_token=settings.GOOGLE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )


def _page(title: str, body: str, color: str = "#00756a") -> HTMLResponse:
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f9fafb;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
    .card{{background:#fff;border-radius:16px;padding:40px 48px;max-width:520px;width:90%;box-shadow:0 4px 24px rgba(0,0,0,.08);text-align:center;}}
    .icon{{font-size:44px;margin-bottom:14px;}}
    h1{{font-size:21px;font-weight:700;color:#111827;margin-bottom:10px;}}
    p{{font-size:14px;color:#6b7280;line-height:1.65;}}
    .btn{{display:inline-block;margin-top:20px;padding:12px 28px;background:{color};color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px;}}
    .slot-list{{list-style:none;margin:18px 0;text-align:left;}}
    .slot-list li{{margin-bottom:9px;}}
    .slot-list a{{display:block;padding:13px 16px;border:1.5px solid #e5e7eb;border-radius:10px;color:#111827;text-decoration:none;font-size:14px;font-weight:500;}}
    .slot-list a:hover{{border-color:{color};background:#f0fdf4;color:{color};}}
    .custom-link{{display:block;margin-top:14px;font-size:13px;color:#9ca3af;}}
    .custom-link a{{color:{color};text-decoration:underline;}}
    .apology{{background:#fff7ed;border-left:4px solid #f97316;padding:12px 16px;border-radius:6px;margin-bottom:18px;font-size:13px;text-align:left;color:#92400e;}}
    label{{font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:5px;text-align:left;}}
    input{{width:100%;padding:10px 14px;border:1.5px solid #e5e7eb;border-radius:8px;font-size:14px;outline:none;margin-bottom:14px;}}
    .submit{{width:100%;padding:12px;background:{color};color:#fff;border:none;border-radius:8px;font-size:15px;font-weight:600;cursor:pointer;margin-top:4px;}}
    .brand{{margin-top:28px;font-size:11px;color:#d1d5db;}}
  </style>
</head>
<body>
  <div class="card">
    {body}
    <div class="brand">Hirix · Powered by Tek Leaders</div>
  </div>
</body>
</html>""")


def _fmt(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%A, %d %B %Y · %I:%M %p IST")
    except Exception:
        return iso


def _find_free_slots(busy: list, search_start: datetime, n: int = 3) -> list[str]:
    busy_ranges = []
    for b in busy:
        s = datetime.fromisoformat(b["start"].replace("Z", "")).replace(tzinfo=None) + IST_OFFSET
        e = datetime.fromisoformat(b["end"].replace("Z", "")).replace(tzinfo=None) + IST_OFFSET
        busy_ranges.append((s, e))

    slots, cur = [], search_start.replace(minute=0, second=0, microsecond=0)
    if cur.hour < BUSINESS_START:
        cur = cur.replace(hour=BUSINESS_START)
    elif cur.hour >= BUSINESS_END:
        cur = (cur + timedelta(days=1)).replace(hour=BUSINESS_START)

    for _ in range(14 * (BUSINESS_END - BUSINESS_START)):
        if len(slots) >= n:
            break
        if cur.weekday() >= 5:
            cur = (cur + timedelta(days=1)).replace(hour=BUSINESS_START)
            continue
        if cur.hour >= BUSINESS_END:
            cur = (cur + timedelta(days=1)).replace(hour=BUSINESS_START)
            continue
        end = cur + timedelta(hours=1)
        if not any(s < end and e > cur for s, e in busy_ranges):
            slots.append(cur.isoformat())
        cur += timedelta(hours=1)
    return slots


async def _busy(cal_svc, start_ist: datetime, end_ist: datetime) -> list:
    def to_utc(dt): return (dt - IST_OFFSET).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = cal_svc.freebusy().query(body={
        "timeMin": to_utc(start_ist),
        "timeMax": to_utc(end_ist),
        "timeZone": "Asia/Kolkata",
        "items": [{"id": "primary"}],
    }).execute()
    return result.get("calendars", {}).get("primary", {}).get("busy", [])


async def _send_slots_email(gmail_svc, candidate_email: str, candidate_name: str,
                             job_title: str, token: str, slots: list[str],
                             slot_duration: int, apology: bool = False):
    import base64
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    base_url = "http://localhost:8000/api/v1"
    slot_items = "".join(
        f'<li><a href="{base_url}/portal/select-slot?token={token}&slot={s}">📅 {_fmt(s)}</a></li>'
        for s in slots
    )
    custom_url = f"{base_url}/portal/custom-slot?token={token}"

    apology_block = ""
    if apology:
        apology_block = '<div class="apology"><b>We apologise</b> — the previously offered slots were taken. Here are the next available ones:</div>'

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:560px;margin:32px auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.07);">

  <div style="background:#1a2d5a;padding:24px 36px;display:flex;align-items:center;gap:16px;">
    <div style="display:inline-flex;align-items:center;font-family:'Arial Black',Arial,sans-serif;font-size:20px;font-weight:900;">
      <span style="background:#c0001d;color:#fff;padding:3px 8px;border-radius:3px 0 0 3px;">Tek</span><span style="background:#fff;color:#1a2d5a;padding:3px 8px;border-radius:0 3px 3px 0;">Leaders</span>
    </div>
    <span style="color:#94a3b8;font-size:13px;">Interview Scheduling</span>
  </div>

  <div style="padding:32px 36px;">
    {apology_block}
    <h2 style="font-size:19px;font-weight:700;color:#111827;margin:0 0 8px;">Choose your interview slot</h2>
    <p style="font-size:14px;color:#6b7280;margin:0 0 20px;">
      Dear <b>{candidate_name}</b>, please select one of the available slots below for the <b>{job_title}</b> interview:
    </p>
    <ul style="list-style:none;padding:0;margin:0 0 20px;">
      {slot_items}
    </ul>
    <p style="font-size:13px;color:#9ca3af;">
      None of these work? <a href="{custom_url}" style="color:#00756a;font-weight:600;">Request a custom time slot →</a>
    </p>
  </div>

  <div style="background:#f9fafb;padding:16px 36px;border-top:1px solid #f0f0f0;font-size:11px;color:#9ca3af;text-align:center;">
    Tek Leaders · recruit@tekleaders.io · Changing The Equation
  </div>
</div>

<style>
  ul a{{display:block;padding:13px 16px;border:1.5px solid #e5e7eb;border-radius:9px;color:#111827;text-decoration:none;font-size:14px;font-weight:500;margin-bottom:9px;}}
  .apology{{background:#fff7ed;border-left:4px solid #f97316;padding:12px 16px;border-radius:6px;margin-bottom:18px;font-size:13px;color:#92400e;}}
</style>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Interview Slot Selection — {job_title} | Tek Leaders"
    msg["To"]      = candidate_email
    msg["From"]    = f"Tek Leaders Recruitment <{settings.GOOGLE_SENDER_EMAIL}>"
    msg.attach(MIMEText(html, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail_svc.users().messages().send(userId="me", body={"raw": raw}).execute()


async def _book_and_confirm(gmail_svc, cal_svc, candidate_email: str, candidate_name: str,
                             job_title: str, slot_iso: str, duration_min: int) -> tuple[str, str]:
    import base64
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    start_ist = datetime.fromisoformat(slot_iso)
    end_ist   = start_ist + timedelta(minutes=duration_min)
    to_utc    = lambda dt: (dt - IST_OFFSET).strftime("%Y-%m-%dT%H:%M:%S") + "Z"

    event = {
        "summary": f"Interview: {candidate_name} — {job_title}",
        "description": f"Candidate interview for {job_title}.\n{candidate_name} ({candidate_email})",
        "start": {"dateTime": to_utc(start_ist), "timeZone": "UTC"},
        "end":   {"dateTime": to_utc(end_ist),   "timeZone": "UTC"},
        "attendees": [{"email": candidate_email}],
        "reminders": {"useDefault": True},
        "conferenceData": {"createRequest": {
            "requestId": str(uuid.uuid4()),
            "conferenceSolutionKey": {"type": "hangoutsMeet"},
        }},
    }
    created   = cal_svc.events().insert(calendarId="primary", body=event,
                                         conferenceDataVersion=1, sendUpdates="all").execute()
    event_id  = created["id"]
    meet_link = created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")
    cal_link  = created.get("htmlLink", "")

    meet_btn = f'<a href="{meet_link}" style="display:inline-block;padding:11px 24px;background:#00756a;color:#fff;border-radius:8px;text-decoration:none;font-weight:700;font-size:14px;margin-top:4px;">Join Google Meet</a>' if meet_link else ""
    cal_btn  = f'<br/><a href="{cal_link}" style="font-size:12px;color:#9ca3af;margin-top:8px;display:inline-block;">View in Google Calendar</a>' if cal_link else ""

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:560px;margin:32px auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.07);">

  <div style="background:#1a2d5a;padding:24px 36px;display:flex;align-items:center;gap:16px;">
    <div style="display:inline-flex;align-items:center;font-family:'Arial Black',Arial,sans-serif;font-size:20px;font-weight:900;">
      <span style="background:#c0001d;color:#fff;padding:3px 8px;border-radius:3px 0 0 3px;">Tek</span><span style="background:#fff;color:#1a2d5a;padding:3px 8px;border-radius:0 3px 3px 0;">Leaders</span>
    </div>
    <span style="color:#94a3b8;font-size:13px;">Interview Confirmed ✅</span>
  </div>

  <div style="padding:32px 36px;">
    <h2 style="font-size:19px;font-weight:700;color:#15803d;margin:0 0 16px;">Your interview is confirmed!</h2>
    <p style="font-size:14px;color:#374151;margin:0 0 20px;">Dear <b>{candidate_name}</b>, your interview for <b>{job_title}</b> has been successfully scheduled.</p>

    <div style="background:#f9fafb;border-radius:10px;padding:20px 24px;margin-bottom:24px;border:1px solid #f0f0f0;">
      <table style="width:100%;font-size:14px;border-collapse:collapse;">
        <tr><td style="color:#9ca3af;padding:5px 0;width:110px;vertical-align:top;">Position</td><td style="font-weight:600;">{job_title}</td></tr>
        <tr><td style="color:#9ca3af;padding:5px 0;vertical-align:top;">Date &amp; Time</td><td style="font-weight:600;">{_fmt(slot_iso)}</td></tr>
        <tr><td style="color:#9ca3af;padding:5px 0;vertical-align:top;">Duration</td><td style="font-weight:600;">{duration_min} minutes</td></tr>
        <tr><td style="color:#9ca3af;padding:5px 0;vertical-align:top;">Company</td><td style="font-weight:600;">Tek Leaders</td></tr>
      </table>
    </div>

    <div style="text-align:center;">
      {meet_btn}
      {cal_btn}
    </div>

    <p style="font-size:12px;color:#9ca3af;margin-top:24px;">A calendar invite has been sent to your email. Please accept it to add the event to your calendar.</p>
  </div>

  <div style="background:#f9fafb;padding:16px 36px;border-top:1px solid #f0f0f0;font-size:11px;color:#9ca3af;text-align:center;">
    Tek Leaders · recruit@tekleaders.io · Changing The Equation
  </div>
</div>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Interview Confirmed — {job_title} · {_fmt(slot_iso)}"
    msg["To"]      = candidate_email
    msg["From"]    = f"Tek Leaders Recruitment <{settings.GOOGLE_SENDER_EMAIL}>"
    msg.attach(MIMEText(html, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail_svc.users().messages().send(userId="me", body={"raw": raw}).execute()

    return event_id, meet_link


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/respond", response_class=HTMLResponse)
async def candidate_respond(token: str, action: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.token == token))
    inv = result.scalar_one_or_none()
    if not inv:
        return _page("Invalid Link", '<div class="icon">⚠️</div><h1>Link not found</h1><p>This invitation link is invalid or has expired.</p>')

    # Capture all needed fields NOW before any commit
    inv_id        = inv.id
    inv_token     = inv.token
    inv_email     = inv.candidate_email
    inv_name      = inv.candidate_name
    inv_job       = inv.job_title
    inv_status    = inv.status
    inv_duration  = inv.slot_duration_minutes or 60

    if action == "not_interested":
        inv.status = "not_interested"
        await db.commit()
        return _page("Response Recorded",
            f'<div class="icon">👋</div><h1>Thank you, {inv_name.split()[0]}!</h1>'
            f'<p>We\'ve noted that you\'re not interested in the <b>{inv_job}</b> role and will keep your profile for future opportunities.</p>',
            color="#6b7280")

    if action != "interested":
        return _page("Invalid Link", '<div class="icon">⚠️</div><h1>Invalid action</h1><p>Please use the buttons in your invitation email.</p>')

    if inv_status != "pending":
        return _page("Already Responded",
            '<div class="icon">ℹ️</div><h1>Already recorded</h1><p>Your response has been recorded. Please check your email for further details.</p>')

    inv.status = "interested"
    await db.commit()

    # Find 3 free slots
    creds     = _get_creds()
    cal_svc   = build("calendar", "v3", credentials=creds)
    gmail_svc = build("gmail", "v1", credentials=creds)

    now_ist      = datetime.utcnow() + IST_OFFSET
    search_start = (now_ist + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0)
    search_end   = search_start + timedelta(days=14)
    busy_periods = await _busy(cal_svc, search_start, search_end)
    slots        = _find_free_slots(busy_periods, search_start, n=3)

    if not slots:
        return _page("No Slots Available",
            '<div class="icon">📞</div><h1>No slots available</h1><p>No availability in the next 2 weeks. Our team will contact you shortly.</p>')

    # Update status to slot_pending — fetch fresh object
    result2 = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.id == inv_id))
    inv2 = result2.scalar_one_or_none()
    if inv2:
        inv2.status = "slot_pending"
        inv2.slots_offered = json.dumps(slots)
        await db.commit()

    await _send_slots_email(gmail_svc, inv_email, inv_name, inv_job, inv_token, slots, inv_duration)

    return _page("Slots Sent!",
        f'<div class="icon">📬</div><h1>Check your inbox!</h1>'
        f'<p>We\'ve sent <b>3 available interview slots</b> to <b>{inv_email}</b>. '
        f'Please select a time that works for you.</p>')


@router.get("/select-slot", response_class=HTMLResponse)
async def select_slot(token: str, slot: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.token == token))
    inv = result.scalar_one_or_none()
    if not inv:
        return _page("Invalid Link", '<div class="icon">⚠️</div><h1>Link not found</h1><p>This invitation link is invalid or has expired.</p>')

    inv_id       = inv.id
    inv_token    = inv.token
    inv_email    = inv.candidate_email
    inv_name     = inv.candidate_name
    inv_job      = inv.job_title
    inv_status   = inv.status
    inv_duration = inv.slot_duration_minutes or 60
    inv_offered  = json.loads(inv.slots_offered or "[]")

    if inv_status == "scheduled":
        return _page("Already Booked", '<div class="icon">✅</div><h1>Already scheduled!</h1><p>Your interview is already confirmed. Please check your email for details.</p>')
    if inv_status != "slot_pending":
        return _page("Link Expired", '<div class="icon">⏰</div><h1>Link expired</h1><p>This slot selection link is no longer valid.</p>')
    if slot not in inv_offered:
        return _page("Invalid Slot", '<div class="icon">⚠️</div><h1>Invalid slot</h1><p>This time slot was not offered. Please use the links in your email.</p>')

    creds     = _get_creds()
    cal_svc   = build("calendar", "v3", credentials=creds)
    gmail_svc = build("gmail", "v1", credentials=creds)

    slot_dt  = datetime.fromisoformat(slot)
    slot_end = slot_dt + timedelta(minutes=inv_duration)
    busy     = await _busy(cal_svc, slot_dt, slot_end)

    if busy:
        # Slot was taken — find new slots
        now_ist      = datetime.utcnow() + IST_OFFSET
        search_start = (now_ist + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0)
        search_end   = search_start + timedelta(days=14)
        all_busy     = await _busy(cal_svc, search_start, search_end)
        new_slots    = _find_free_slots(all_busy, search_start, n=3)

        result2 = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.id == inv_id))
        inv2 = result2.scalar_one_or_none()
        if inv2:
            inv2.slots_offered = json.dumps(new_slots)
            inv2.custom_slot_attempts = (inv2.custom_slot_attempts or 0) + 1
            await db.commit()

        if new_slots:
            await _send_slots_email(gmail_svc, inv_email, inv_name, inv_job, inv_token, new_slots, inv_duration, apology=True)
            return _page("Slot Taken",
                f'<div class="icon">😔</div><h1>That slot was just taken</h1>'
                f'<p>We apologise — new slots have been sent to <b>{inv_email}</b>.</p>', color="#f97316")
        else:
            return _page("No Slots Available",
                '<div class="icon">📞</div><h1>No slots available</h1><p>Our recruiter will contact you directly to schedule your interview.</p>', color="#f97316")

    event_id, meet_link = await _book_and_confirm(gmail_svc, cal_svc, inv_email, inv_name, inv_job, slot, inv_duration)

    result3 = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.id == inv_id))
    inv3 = result3.scalar_one_or_none()
    if inv3:
        inv3.status = "scheduled"
        inv3.selected_slot = slot
        inv3.calendar_event_id = event_id
        inv3.meet_link = meet_link
        await db.commit()

    meet_btn = f'<a href="{meet_link}" class="btn" style="margin-top:16px;">Join Google Meet</a>' if meet_link else ""
    return _page("Interview Booked!",
        f'<div class="icon">🎉</div><h1>Interview confirmed!</h1>'
        f'<p>Your interview for <b>{inv_job}</b> is confirmed for<br/><b>{_fmt(slot)}</b>.</p>'
        f'<p style="margin-top:10px;">A confirmation email has been sent to <b>{inv_email}</b>.</p>{meet_btn}')


@router.get("/custom-slot", response_class=HTMLResponse)
async def custom_slot_form(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.token == token))
    inv = result.scalar_one_or_none()
    if not inv or inv.status != "slot_pending":
        return _page("Invalid Link", '<div class="icon">⚠️</div><h1>Link not found</h1><p>This link is invalid or has expired.</p>')

    tomorrow = (datetime.utcnow() + IST_OFFSET + timedelta(days=1)).strftime("%Y-%m-%d")
    return _page("Request Custom Slot", f"""
    <div class="icon">📅</div>
    <h1>Request a custom slot</h1>
    <p style="margin-bottom:22px;">None of the offered slots work? Suggest a preferred time and we'll check availability.</p>
    <form method="POST" action="/api/v1/portal/custom-slot">
      <input type="hidden" name="token" value="{token}"/>
      <label>Preferred Date</label>
      <input type="date" name="date" min="{tomorrow}" required/>
      <label>Preferred Time (IST, 9 AM – 6 PM)</label>
      <input type="time" name="time" min="09:00" max="17:00" required/>
      <button type="submit" class="submit">Request This Slot</button>
    </form>""")


@router.post("/custom-slot", response_class=HTMLResponse)
async def custom_slot_submit(token: str = Form(...), date: str = Form(...), time: str = Form(...),
                              db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.token == token))
    inv = result.scalar_one_or_none()
    if not inv or inv.status != "slot_pending":
        return _page("Invalid Link", '<div class="icon">⚠️</div><h1>Link not found</h1><p>This link is invalid or has expired.</p>')

    inv_id       = inv.id
    inv_token    = inv.token
    inv_email    = inv.candidate_email
    inv_name     = inv.candidate_name
    inv_job      = inv.job_title
    inv_duration = inv.slot_duration_minutes or 60

    try:
        slot_dt = datetime.fromisoformat(f"{date}T{time}:00")
    except ValueError:
        return _page("Invalid Date", '<div class="icon">⚠️</div><h1>Invalid date/time</h1><p>Please go back and enter a valid date and time.</p>')

    creds     = _get_creds()
    cal_svc   = build("calendar", "v3", credentials=creds)
    gmail_svc = build("gmail", "v1", credentials=creds)

    busy = await _busy(cal_svc, slot_dt, slot_dt + timedelta(minutes=inv_duration))

    if busy:
        search_start = (slot_dt + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0)
        search_end   = search_start + timedelta(days=14)
        all_busy     = await _busy(cal_svc, search_start, search_end)
        new_slots    = _find_free_slots(all_busy, search_start, n=3)

        result2 = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.id == inv_id))
        inv2 = result2.scalar_one_or_none()
        if inv2:
            inv2.slots_offered = json.dumps(new_slots)
            inv2.custom_slot_attempts = (inv2.custom_slot_attempts or 0) + 1
            await db.commit()

        if new_slots:
            await _send_slots_email(gmail_svc, inv_email, inv_name, inv_job, inv_token, new_slots, inv_duration, apology=True)
            return _page("Slot Unavailable",
                f'<div class="icon">😔</div><h1>That time is not available</h1>'
                f'<p>We apologise — new available slots have been sent to <b>{inv_email}</b>.</p>', color="#f97316")
        else:
            return _page("No Slots Available",
                '<div class="icon">📞</div><h1>No slots available</h1><p>Our recruiter will contact you directly.</p>', color="#f97316")

    slot_iso = slot_dt.isoformat()
    event_id, meet_link = await _book_and_confirm(gmail_svc, cal_svc, inv_email, inv_name, inv_job, slot_iso, inv_duration)

    result3 = await db.execute(select(InterviewInvitationModel).where(InterviewInvitationModel.id == inv_id))
    inv3 = result3.scalar_one_or_none()
    if inv3:
        inv3.status = "scheduled"
        inv3.selected_slot = slot_iso
        inv3.calendar_event_id = event_id
        inv3.meet_link = meet_link
        await db.commit()

    meet_btn = f'<a href="{meet_link}" class="btn" style="margin-top:16px;">Join Google Meet</a>' if meet_link else ""
    return _page("Interview Booked!",
        f'<div class="icon">🎉</div><h1>Interview confirmed!</h1>'
        f'<p>Your interview for <b>{inv_job}</b> is confirmed for<br/><b>{_fmt(slot_iso)}</b>.</p>'
        f'<p style="margin-top:10px;">A confirmation has been sent to <b>{inv_email}</b>.</p>{meet_btn}')
