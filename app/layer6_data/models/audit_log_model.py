from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class AuditAction(str, enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    AI_DECISION = "ai_decision"
    HUMAN_OVERRIDE = "human_override"
    STAGE_CHANGE = "stage_change"
    EXPORT = "export"

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)   # null = system
    company_id = Column(String, ForeignKey("companies.id"), nullable=True, index=True)
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(String, nullable=False)       # e.g. "application", "job"
    resource_id = Column(String, nullable=True, index=True)
    old_value = Column(Text, nullable=True)              # JSON snapshot before
    new_value = Column(Text, nullable=True)              # JSON snapshot after
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    correlation_id = Column(String, nullable=True, index=True)  # trace ID
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
