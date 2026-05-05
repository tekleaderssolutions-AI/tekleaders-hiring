from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.layer6_data.models.base import Base

class CandidateEvaluationModel(Base):
    """
    AI SCORING LAYER
    Provides explainable AI evaluations for a specific application.
    Debuggable and transparent matching.
    """
    __tablename__ = "candidate_evaluations"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    
    # Granular Scoring
    skills_score = Column(Float, nullable=True)     # Match on hard/soft skills
    experience_score = Column(Float, nullable=True) # Match on years/seniority
    semantic_score = Column(Float, nullable=True)   # Vector similarity score
    culture_fit_score = Column(Float, nullable=True)
    
    final_score = Column(Float, nullable=True)      # Weighted average
    
    # Explainability
    reasoning = Column(Text, nullable=True)         # AI explanation of the score
    strengths = Column(JSON, nullable=True)         # Elite Layer: matching highlights
    gaps = Column(JSON, nullable=True)              # Elite Layer: missing requirements
    
    # Metadata
    model_version = Column(String, nullable=True)   # e.g. "gpt-4o-2024-05-13"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    application = relationship("ApplicationModel", back_populates="evaluations")
