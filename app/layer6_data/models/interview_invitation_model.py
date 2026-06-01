from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.sql import func
from app.layer6_data.models.base import Base


class InterviewInvitationModel(Base):
    __tablename__ = "interview_invitations"

    id = Column(String, primary_key=True)
    token = Column(String, unique=True, nullable=False, index=True)

    candidate_email = Column(String, nullable=False)
    candidate_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_id = Column(String, nullable=True, index=True)
    recruiter_id = Column(String, nullable=True, index=True)
    jd_details = Column(Text, nullable=True)       # JSON: {skills, experience, description}
    recruiter_name = Column(String, nullable=True)
    company_name = Column(String, default="Tek Leaders")

    # Workflow state: pending → interested / not_interested → slot_pending → scheduled
    status = Column(String, default="pending")

    slots_offered = Column(Text, nullable=True)    # JSON array of ISO datetimes
    slot_duration_minutes = Column(Integer, default=60)
    selected_slot = Column(String, nullable=True)  # ISO datetime chosen by candidate
    calendar_event_id = Column(String, nullable=True)
    meet_link = Column(String, nullable=True)
    custom_slot_attempts = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
