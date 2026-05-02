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

class WorkplaceType(str, enum.Enum):
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    REMOTE = "remote"

class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # 1. Job title and department
    title = Column(String, nullable=False, index=True)
    job_code = Column(String, nullable=True)
    department = Column(String, nullable=True)
    
    # 2. Location
    workplace_type = Column(Enum(WorkplaceType), default=WorkplaceType.ON_SITE)
    location = Column(String, nullable=True)
    
    # 3. Description
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    
    # 4. Industry & Function
    company_industry = Column(String, nullable=True)
    job_function = Column(String, nullable=True)
    
    # 5. Employment details
    employment_type = Column(Enum(EmploymentType), nullable=False)
    experience_level = Column(Enum(ExperienceLevel), nullable=False)
    education = Column(String, nullable=True)
    keywords = Column(JSON, nullable=True) # Replaces required_skills to match UI
    
    # 6. Annual salary
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String, default="INR")
    
    # System fields
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT)
    published_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("CompanyModel", back_populates="jobs")
    applications = relationship("ApplicationModel", back_populates="job")
