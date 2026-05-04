from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

@dataclass
class CandidateExperience:
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False

@dataclass
class CandidateEducation:
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@dataclass
class Candidate:
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    
    # AI Extracted fields
    skills: List[str] = field(default_factory=list)
    experience: List[CandidateExperience] = field(default_factory=list)
    education: List[CandidateEducation] = field(default_factory=list)
    
    # Matching metadata
    total_years_experience: float = 0.0
    top_skills: List[str] = field(default_factory=list)
    
    # System fields
    memory_id: Optional[str] = None  # Reference to Vector DB
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
