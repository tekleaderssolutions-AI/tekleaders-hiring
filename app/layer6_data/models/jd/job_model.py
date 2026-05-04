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
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"

class ExperienceLevel(str, enum.Enum):
    ENTRY_LEVEL = "Entry Level"
    MID_LEVEL = "Mid Level"
    SENIOR_LEVEL = "Senior Level"
    DIRECTOR = "Director"
    EXECUTIVE = "Executive"
    INTERNSHIP = "Internship"

class WorkplaceType(str, enum.Enum):
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    REMOTE = "remote"

class CompanyIndustry(str, enum.Enum):
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCE = "Finance"
    EDUCATION = "Education"
    MANUFACTURING = "Manufacturing"
    RETAIL = "Retail"
    CONSULTING = "Consulting"
    ENERGY = "Energy"
    MEDIA_ENTERTAINMENT = "Media & Entertainment"
    REAL_ESTATE = "Real Estate"

class JobFunction(str, enum.Enum):
    ENGINEERING = "Engineering"
    PRODUCT_MANAGEMENT = "Product Management"
    DESIGN = "Design"
    SALES = "Sales"
    MARKETING = "Marketing"
    HUMAN_RESOURCES = "Human Resources"
    FINANCE = "Finance"
    LEGAL = "Legal"
    OPERATIONS = "Operations"
    CUSTOMER_SUPPORT = "Customer Support"

class EducationLevel(str, enum.Enum):
    HIGH_SCHOOL = "High School"
    ASSOCIATES = "Associate's Degree"
    BACHELORS = "Bachelor's Degree"
    MASTERS = "Master's Degree"
    PHD = "PhD"
    NONE = "None"

class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=True, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # 1. Job title and department
    title = Column(String, nullable=False, index=True)
    job_code = Column(String, nullable=True)
    short_id = Column(String, nullable=True, index=True) # e.g. tek0001
    department = Column(String, nullable=True)
    team = Column(String, nullable=True)
    
    # 2. Location
    workplace_type = Column(Enum(WorkplaceType), default=WorkplaceType.ON_SITE)
    location = Column(String, nullable=True)
    
    # 3. Description
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    
    # 4. Industry & Function
    industry = Column(Enum(CompanyIndustry), nullable=True)
    job_function = Column(Enum(JobFunction), nullable=True)
    
    # 5. Employment details
    employment_type = Column(Enum(EmploymentType), nullable=False)
    experience_level = Column(Enum(ExperienceLevel), nullable=False)
    education_level = Column(Enum(EducationLevel), nullable=True)
    primary_skills = Column(JSON, nullable=True) 
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
