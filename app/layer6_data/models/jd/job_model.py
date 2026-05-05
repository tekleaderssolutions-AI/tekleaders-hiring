from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer, func
from sqlalchemy.orm import relationship
import enum

from app.layer6_data.models.base import Base

class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class JobModel(Base):
    """
    GLOBAL JOB IDENTITY
    The stable reference for a hiring role at a company.
    One Job = One Identity (e.g. TEK-001).
    Versioning happens via JobVersionModel.
    """
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=True, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Stable Identifiers
    job_code = Column(String, nullable=True, index=True) # e.g. TEK-001
    short_id = Column(String, nullable=True, index=True) # e.g. tek0001
    
    # Snapshot of Current State (for performance)
    current_title = Column(String, nullable=True, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT)
    
    # System fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("CompanyModel", back_populates="jobs")
    versions = relationship("JobVersionModel", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("ApplicationModel", back_populates="job")
