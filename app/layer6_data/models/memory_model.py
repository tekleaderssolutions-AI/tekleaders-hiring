from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey, Integer, Boolean, func
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from app.layer6_data.models.base import Base

class MemoryModel(Base):
    """
    PRODUCTION-GRADE VECTOR LAYER
    Supports chunked document storage, multi-tenant isolation, 
    and embedding model versioning.
    """
    __tablename__ = "memories"

    id = Column(String, primary_key=True, index=True)
    short_id = Column(String, index=True, nullable=True) # e.g. tek0001
    
    # ─── Context Isolation ──────────────────────────────────────────────────
    entity_type = Column(String, nullable=False, index=True) # 'resume_chunk' or 'job_chunk'
    company_id = Column(String, ForeignKey("companies.id"), nullable=True, index=True) # CRITICAL for multi-tenancy
    cluster = Column(String, index=True, nullable=True)     # e.g. 'data_science', 'backend'
    
    # ─── Linking ────────────────────────────────────────────────────────────
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=True, index=True)
    job_version_id = Column(String, ForeignKey("job_versions.id"), nullable=True, index=True)
    
    # ─── Chunking Strategy ──────────────────────────────────────────────────
    chunk_type = Column(String, index=True) # e.g. 'summary', 'skills', 'experience_item'
    chunk_index = Column(Integer, default=0) # Order of chunks within the document
    text = Column(Text, nullable=False)      # The actual text chunk
    
    # ─── Embedding Intelligence ─────────────────────────────────────────────
    embedding = Column(Vector(1536), nullable=False) # Vector data
    embedding_model = Column(String, default="text-embedding-3-small") # PRIORITY 2: Versioning
    embedding_version = Column(String, default="1.0")
    
    # ─── Status & Lifecycle ────────────────────────────────────────────────
    is_active = Column(Boolean, default=True, index=True) # PRIORITY 2: Lifecycle management
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = relationship("ResumeModel", back_populates="memories")
    job_version = relationship("JobVersionModel", back_populates="memories")
