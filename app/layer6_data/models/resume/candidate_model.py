from sqlalchemy import Column, String, DateTime, JSON, Float, Boolean, func

from sqlalchemy.orm import relationship
from app.layer6_data.models.base import Base

class CandidateModel(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    location = Column(String)
    summary = Column(String)
    
    # Structured Data (Stored as JSONB in Postgres)
    skills = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    education = Column(JSON, default=list)
    
    total_years_experience = Column(Float, default=0.0)
    
    # Matching Reference
    memory_id = Column(String, index=True) # ID in Vector DB
    
    candidate_metadata = Column(JSON, default=dict)
    
    # Relationships
    applications = relationship("ApplicationModel", back_populates="candidate")
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
