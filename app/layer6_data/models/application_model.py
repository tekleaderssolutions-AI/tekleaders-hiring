from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, Enum, JSON, UniqueConstraint, func
from sqlalchemy.orm import relationship
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
    """
    CONTEXT LAYER
    The central junction connecting Candidate, Resume Version, Job, and Company.
    Enables multi-role and multi-client support for the same candidate.
    """
    __tablename__ = "applications"

    id = Column(String, primary_key=True, index=True)
    
    # Core Connections
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    job_version_id = Column(String, ForeignKey("job_versions.id"), nullable=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    
    # Lifecycle
    current_stage = Column(Enum(ApplicationStage), default=ApplicationStage.APPLIED)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.ACTIVE)
    
    # Intelligence Data (Cached for quick listing)
    match_score = Column(Float, nullable=True)          # 0-100
    score_breakdown = Column(JSON, nullable=True)       # {skills: 80, experience: 70, semantic: 90}
    
    # Metadata
    source = Column(String, nullable=True)               # e.g. "careers_portal", "referral"
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Constraints: One candidate can apply to one job only once
    __table_args__ = (UniqueConstraint('candidate_id', 'job_id', name='_candidate_job_uc'),)

    # Relationships
    candidate = relationship("CandidateModel", back_populates="applications")
    resume = relationship("ResumeModel", back_populates="applications")
    job = relationship("JobModel", back_populates="applications")
    job_version = relationship("JobVersionModel", back_populates="applications")
    evaluations = relationship("CandidateEvaluationModel", back_populates="application", cascade="all, delete-orphan")
    feedback = relationship("ApplicationFeedbackModel", back_populates="application", uselist=False)
