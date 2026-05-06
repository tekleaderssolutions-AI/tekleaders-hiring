from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Any
from datetime import datetime
from app.layer6_data.models.jd.job_model import (
    EmploymentType, ExperienceLevel, WorkplaceType, JobStatus, 
    CompanyIndustry, JobFunction, EducationLevel
)

def normalize_enum_value(value: Any, enum_class: Any) -> Any:
    """Helper to convert UI strings to Enum members."""
    if not value:
        return None
    if isinstance(value, enum_class):
        return value
    if isinstance(value, str):
        # Normalize: 'Full Time' -> 'full_time'
        normalized = value.lower().strip().replace(" ", "_")
        # Try to find match in Enum
        for member in enum_class:
            if member.value == normalized:
                return member
    return value # Let Pydantic handle the error if no match found

class JobCreate(BaseModel):
    title: str = Field(..., max_length=80)
    job_code: Optional[str] = None
    department: Optional[str] = None
    
    workplace_type: Any = WorkplaceType.ON_SITE
    location: Optional[str] = None
    
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    
    industry: Any = None
    job_function: Any = None
    
    employment_type: Any
    experience_level: Any
    education_level: Any = None
    keywords: Optional[List[str] | str] = []
    
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "INR"
    status: Any = JobStatus.DRAFT

    @model_validator(mode='before')
    @classmethod
    def process_enums(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
            
        # Map of field names to their respective Enum classes
        mapping = {
            "industry": CompanyIndustry,
            "job_function": JobFunction,
            "employment_type": EmploymentType,
            "experience_level": ExperienceLevel,
            "education_level": EducationLevel,
            "workplace_type": WorkplaceType,
            "status": JobStatus
        }
        
        for field, enum_cls in mapping.items():
            if field in data:
                data[field] = normalize_enum_value(data[field], enum_cls)
        
        return data

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=80)
    job_code: Optional[str] = None
    department: Optional[str] = None
    workplace_type: Optional[Any] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[Any] = None
    job_function: Optional[Any] = None
    employment_type: Optional[Any] = None
    experience_level: Optional[Any] = None
    education_level: Optional[Any] = None
    keywords: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    status: Optional[Any] = None

    @model_validator(mode='before')
    @classmethod
    def process_enums(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        mapping = {
            "industry": CompanyIndustry,
            "job_function": JobFunction,
            "employment_type": EmploymentType,
            "experience_level": ExperienceLevel,
            "education_level": EducationLevel,
            "workplace_type": WorkplaceType,
            "status": JobStatus
        }
        for field, enum_cls in mapping.items():
            if field in data:
                data[field] = normalize_enum_value(data[field], enum_cls)
        return data

class JobRead(BaseModel):
    id: str
    company_id: str
    created_by: str
    title: str
    job_code: Optional[str] = None
    department: Optional[str] = None
    workplace_type: Any = None
    location: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    industry: Optional[Any] = None
    job_function: Optional[Any] = None
    employment_type: Any
    experience_level: Any
    education_level: Optional[Any] = None
    keywords: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    status: Any = None
    created_at: Any = None
    updated_at: Any = None

    class Config:
        from_attributes = True
        # Allow population by field name even if types are slightly mismatched
        populate_by_name = True
