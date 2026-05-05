from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, JSON, func
from sqlalchemy.orm import relationship
from app.layer6_data.models.base import Base

class ResumeModel(Base):
    """
    VERSIONED DOCUMENT LAYER
    Represents a specific version of a candidate's resume.
    One candidate -> multiple resumes (versioned).
    AI embeddings are tied to this level.
    """
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
    
    title = Column(String, nullable=True)          # e.g. "Software Engineer - Backend"
    raw_text = Column(Text, nullable=True)         # PII redacted text
    file_url = Column(String, nullable=True)       # Path to S3/Storage
    
    # Versioning & Deduplication
    version = Column(Integer, default=1)
    content_hash = Column(String, index=True)      # SHA-256 for deduplication
    is_active = Column(Boolean, default=True, index=True) # For version lifecycle
    
    # Embedding Metadata (Priority 2)
    embedding_model = Column(String, nullable=True)
    embedding_version = Column(String, nullable=True)
    
    # Extracted Data (Snapshotted for this version)
    skills_json = Column(JSON, nullable=True)      # Mapped & Normalized skills
    experience_json = Column(JSON, nullable=True)  # Structured experience history
    education_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)    # Seniority, notice period, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    candidate = relationship("CandidateModel", back_populates="resumes")
    applications = relationship("ApplicationModel", back_populates="resume")
    memories = relationship("MemoryModel", back_populates="resume", cascade="all, delete-orphan")
