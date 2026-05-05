from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from app.layer6_data.models.base import Base

class CandidateModel(Base):
    """
    GLOBAL IDENTITY LAYER
    Represents a unique person across the entire Hirix platform.
    One candidate = one identity (email unique).
    """
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    
    # System Fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resumes = relationship("ResumeModel", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("ApplicationModel", back_populates="candidate")
