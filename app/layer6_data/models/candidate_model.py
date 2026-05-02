from sqlalchemy import Column, String, Text, DateTime, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class CandidateStatus(str, enum.Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    HIRED = "hired"
    BLACKLISTED = "blacklisted"

class CandidateModel(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    resume_url = Column(String, nullable=True)           # S3 path
    skills = Column(JSON, nullable=True)                 # list of skill strings
    experience_years = Column(Float, nullable=True)
    education = Column(JSON, nullable=True)              # list of {degree, institution, year}
    status = Column(Enum(CandidateStatus), default=CandidateStatus.ACTIVE)
    embedding_vector_id = Column(String, nullable=True)  # Pinecone vector ID
    source = Column(String, nullable=True)               # e.g. "careers_portal", "linkedin"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    applications = relationship("ApplicationModel", back_populates="candidate")
