from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Any
from datetime import datetime
from app.layer6_data.models.jd.job_model import (
    EmploymentType, ExperienceLevel, WorkplaceType, JobStatus, 
    CompanyIndustry, JobFunction, EducationLevel
)

class JobCreate(BaseModel):
    title: str = Field(..., max_length=80)
    job_code: Optional[str] = None
    department: Optional[str] = None
    
    workplace_type: WorkplaceType = WorkplaceType.ON_SITE
    location: Optional[str] = None
    
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    
    industry: Optional[CompanyIndustry] = None
    job_function: Optional[JobFunction] = None
    
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    education_level: Optional[EducationLevel] = None
    keywords: Optional[List[str] | str] = []
    
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "INR"
    status: Optional[JobStatus] = JobStatus.DRAFT

    @model_validator(mode='before')
    @classmethod
    def normalize_enums(cls, data: Any) -> Any:
        """
        ELITE NORMALIZER: 
        Automatically converts 'Full Time' -> 'full_time', 'Finance' -> 'finance', etc.
        This prevents UI validation errors.
        """
        if isinstance(data, dict):
            enum_fields = [
                "industry", "job_function", "employment_type", 
                "experience_level", "education_level", "workplace_type"
            ]
            for field in enum_fields:
                val = data.get(field)
                if isinstance(val, str):
                    # Lowercase and replace space with underscore
                    data[field] = val.lower().strip().replace(" ", "_")
        return data

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=80)
    job_code: Optional[str] = None
    department: Optional[str] = None
    workplace_type: Optional[WorkplaceType] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[CompanyIndustry] = None # Fixed field name consistency
    job_function: Optional[JobFunction] = None
    employment_type: Optional[EmploymentType] = None
    experience_level: Optional[ExperienceLevel] = None
    education_level: Optional[EducationLevel] = None
    keywords: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    status: Optional[JobStatus] = None

    @model_validator(mode='before')
    @classmethod
    def normalize_enums(cls, data: Any) -> Any:
        if isinstance(data, dict):
            enum_fields = [
                "industry", "job_function", "employment_type", 
                "experience_level", "education_level", "workplace_type"
            ]
            for field in enum_fields:
                val = data.get(field)
                if isinstance(val, str):
                    data[field] = val.lower().strip().replace(" ", "_")
        return data

class JobRead(BaseModel):
    id: str
    company_id: str
    created_by: str
    title: str
    job_code: Optional[str]
    department: Optional[str]
    workplace_type: WorkplaceType
    location: Optional[str]
    description: str
    requirements: Optional[str]
    benefits: Optional[str]
    industry: Optional[CompanyIndustry]
    job_function: Optional[JobFunction]
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    education_level: Optional[EducationLevel]
    keywords: Optional[List[str]]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: Optional[str]
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
