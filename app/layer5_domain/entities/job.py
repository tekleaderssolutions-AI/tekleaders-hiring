from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
import uuid

@dataclass
class Job:
    title: str
    description: str
    employment_type: str
    experience_level: str
    company_id: str
    created_by: str
    
    id: Optional[str] = None
    job_code: Optional[str] = None
    department: Optional[str] = None
    
    workplace_type: str = "on_site"
    location: Optional[str] = None
    
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    
    company_industry: Optional[str] = None
    job_function: Optional[str] = None
    
    education: Optional[str] = None
    keywords: Optional[List[str]] = field(default_factory=list)
    
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "INR"
    
    status: str = "draft"
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.id:
            self.id = f"job_{uuid.uuid4().hex[:12]}"
