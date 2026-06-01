from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, Enum, JSON, UniqueConstraint, func
from sqlalchemy.orm import relationship
import enum

from app.layer6_data.models.base import Base


class SubmissionStatus(str, enum.Enum):
    ACTIVE = "active"
    DUPLICATE = "duplicate"
    WITHDRAWN = "withdrawn"


class CandidateRanking(str, enum.Enum):
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CandidateSubmissionModel(Base):
    """
    RECRUITER SUBMISSION LAYER
    Tracks every candidate submission by every recruiter per JD.
    Enforces first-come-first-serve duplicate detection.
    """
    __tablename__ = "candidate_submissions"

    id = Column(String, primary_key=True, index=True)

    # Core relationships
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=True, index=True)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=True, index=True)
    submitted_by = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)

    # Candidate info (captured at submission time)
    candidate_name = Column(String, nullable=True)
    candidate_email = Column(String, nullable=True, index=True)
    candidate_phone = Column(String, nullable=True)
    candidate_linkedin = Column(String, nullable=True)
    experience_years = Column(Float, nullable=True)
    current_company = Column(String, nullable=True)
    current_location = Column(String, nullable=True)
    notice_period = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)

    # Recruiter assessment
    ranking = Column(Enum(CandidateRanking), nullable=True)
    notes = Column(Text, nullable=True)

    # Duplicate tracking
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.ACTIVE, index=True)
    duplicate_of = Column(String, ForeignKey("candidate_submissions.id"), nullable=True)

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # One candidate per job (first-come-first-serve)
    __table_args__ = (UniqueConstraint("job_id", "candidate_email", name="_job_email_uc"),)

    # Relationships
    job = relationship("JobModel", back_populates="submissions")
    submitter = relationship("UserModel", foreign_keys=[submitted_by])
