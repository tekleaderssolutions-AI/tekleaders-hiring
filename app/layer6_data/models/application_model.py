from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class ApplicationStage(str, enum.Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class ApplicationStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ON_HOLD = "on_hold"

class ApplicationModel(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    current_stage = Column(Enum(ApplicationStage), default=ApplicationStage.APPLIED)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.ACTIVE)
    source = Column(String, nullable=True)               # e.g. "careers_portal", "referral"
    resume_snapshot_url = Column(String, nullable=True)  # S3 path at time of application
    cover_letter = Column(Text, nullable=True)
    ai_score = Column(Float, nullable=True)              # 0-100 AI match score
    ai_decision = Column(String, nullable=True)          # SHORTLISTED / REJECTED / REVIEW
    stage_history = Column(JSON, nullable=True)          # list of {stage, changed_at, by}
    metadata_ = Column("metadata", JSON, nullable=True)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("CandidateModel", back_populates="applications")
    job = relationship("JobModel", back_populates="applications")
    interviews = relationship("InterviewModel", back_populates="application")
    ai_decisions = relationship("AIDecisionModel", back_populates="application")
