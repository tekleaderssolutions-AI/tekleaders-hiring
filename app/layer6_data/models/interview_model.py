from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class InterviewType(str, enum.Enum):
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"
    HR = "hr"
    FINAL = "final"

class InterviewStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class FeedbackStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    OVERDUE = "overdue"

class InterviewModel(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    type = Column(Enum(InterviewType), nullable=False)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.SCHEDULED)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Float, default=60)
    meeting_url = Column(String, nullable=True)
    interviewer_ids = Column(JSON, nullable=True)        # list of user IDs
    overall_score = Column(Float, nullable=True)         # 0-10
    feedback_status = Column(Enum(FeedbackStatus), default=FeedbackStatus.PENDING)
    feedback_notes = Column(Text, nullable=True)
    recording_url = Column(String, nullable=True)        # S3 path
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    application = relationship("ApplicationModel", back_populates="interviews")
