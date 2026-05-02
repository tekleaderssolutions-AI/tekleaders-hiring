from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: Optional[str]
    email: str
    hashed_password: Optional[str]
    first_name: str
    last_name: str
    company_id: Optional[str] = None
    role: str = "recruiter"
    google_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
