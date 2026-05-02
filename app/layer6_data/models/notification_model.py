from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class NotificationType(str, enum.Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"

class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    recipient_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=True, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    template_id = Column(String, nullable=True)
    template_vars = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
