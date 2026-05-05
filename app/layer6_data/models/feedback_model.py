import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float, Enum, JSON, func
from sqlalchemy.orm import relationship
from app.layer6_data.models.base import Base

class FeedbackOutcome(str, enum.Enum):
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    HIRED = "hired"
    INTERVIEW = "interview"
    SAVED = "saved"

class ApplicationFeedbackModel(Base):
    """
    ELITE LAYER: THE LEARNING LOOP
    Captures recruiter feedback on AI decisions to improve future matching.
    """
    __tablename__ = "application_feedback"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, unique=True)
    recruiter_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Outcomes
    outcome = Column(Enum(FeedbackOutcome), nullable=False)
    
    # Recruiter Override
    recruiter_score = Column(Float, nullable=True) # Manual correction of AI score
    recruiter_notes = Column(Text, nullable=True)  # "Why did you reject/shortlist?"
    
    # Structured Feedback (e.g. "Missing specific skill X")
    feedback_tags = Column(JSON, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    application = relationship("ApplicationModel", back_populates="feedback")
