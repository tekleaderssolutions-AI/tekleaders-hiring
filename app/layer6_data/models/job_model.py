from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"

class ExperienceLevel(str, enum.Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"

class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)
    is_remote = Column(Boolean, default=False)
    employment_type = Column(Enum(EmploymentType), nullable=False)
    experience_level = Column(Enum(ExperienceLevel), nullable=False)
    required_skills = Column(JSON, nullable=True)       # list of skill strings
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String, default="USD")
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT)
    published_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("CompanyModel", back_populates="jobs")
    applications = relationship("ApplicationModel", back_populates="job")
