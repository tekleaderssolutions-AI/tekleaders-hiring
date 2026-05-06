from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON, Boolean, func
from sqlalchemy.orm import relationship
from app.layer6_data.models.base import Base

class JobVersionModel(Base):
    """
    VERSIONED JD LAYER
    Represents a specific version of a Job Description.
    Allows clients to update requirements mid-hiring while preserving history.
    """
    __tablename__ = "job_versions"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Versioned Content
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements_json = Column(JSON, nullable=True) # Structured requirements
    
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True, index=True)
    
    # Embedding Metadata (Priority 2)
    embedding_model = Column(String, nullable=True)
    embedding_version = Column(String, nullable=True)
    
    # Elite Layer: AI-Driven Scoring Strategy
    # e.g. {"semantic_weight": 0.4, "skills_weight": 0.6, "experience_multiplier": 1.2}
    scoring_weights = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    job = relationship("JobModel", back_populates="versions")
    memories = relationship("MemoryModel", back_populates="job_version")
    applications = relationship("ApplicationModel", back_populates="job_version")
