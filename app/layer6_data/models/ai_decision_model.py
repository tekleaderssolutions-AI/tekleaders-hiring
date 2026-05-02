from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class AIDecisionType(str, enum.Enum):
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    INTERVIEW_RECOMMENDED = "INTERVIEW_RECOMMENDED"
    OFFER_RECOMMENDED = "OFFER_RECOMMENDED"

class DecisionSource(str, enum.Enum):
    AI_RULES = "AI-RULES"
    AI_LLM = "AI-LLM"
    HUMAN_OVERRIDE = "HUMAN_OVERRIDE"
    SYSTEM = "SYSTEM"

class AIDecisionModel(Base):
    __tablename__ = "ai_decisions"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    decision = Column(Enum(AIDecisionType), nullable=False)
    score = Column(Float, nullable=True)                 # 0-100
    confidence = Column(Float, nullable=True)            # 0.0-1.0
    reasoning = Column(Text, nullable=True)              # AI reasoning trace (JSON as text)
    decision_source = Column(Enum(DecisionSource), default=DecisionSource.AI_RULES)
    human_review_required = Column(String, default="false")
    human_reviewer_id = Column(String, ForeignKey("users.id"), nullable=True)
    human_override_reason = Column(Text, nullable=True)
    agent_outputs = Column(JSON, nullable=True)          # raw outputs from all agents
    event_id = Column(String, nullable=True, index=True) # correlation to Kafka event
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    application = relationship("ApplicationModel", back_populates="ai_decisions")
