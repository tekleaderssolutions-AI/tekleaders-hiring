from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.layer6_data.models.job_model import EmploymentType, ExperienceLevel, WorkplaceType, JobStatus, CompanyIndustry, JobFunction, EducationLevel

class JobCreate(BaseModel):
    title: str = Field(..., max_length=80)
    job_code: Optional[str] = None
    department: Optional[str] = None
    
    workplace_type: WorkplaceType = WorkplaceType.ON_SITE
    location: Optional[str] = None
    
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    
    company_industry: Optional[CompanyIndustry] = None
    job_function: Optional[JobFunction] = None
    
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    education: Optional[EducationLevel] = None
    keywords: Optional[List[str]] = []
    
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "INR"
    status: Optional[JobStatus] = JobStatus.DRAFT

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=80)
    job_code: Optional[str] = None
    department: Optional[str] = None
    workplace_type: Optional[WorkplaceType] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    company_industry: Optional[CompanyIndustry] = None
    job_function: Optional[JobFunction] = None
    employment_type: Optional[EmploymentType] = None
    experience_level: Optional[ExperienceLevel] = None
    education: Optional[EducationLevel] = None
    keywords: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    status: Optional[JobStatus] = None

class JobRead(JobCreate):
    id: str
    company_id: str
    created_by: str
    status: JobStatus
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
