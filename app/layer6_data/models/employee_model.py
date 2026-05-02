from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class EmploymentStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    RESIGNED = "resigned"
    TERMINATED = "terminated"

class EmployeeModel(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=True)  # if hired from pipeline
    department = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    manager_id = Column(String, ForeignKey("employees.id"), nullable=True)
    employment_status = Column(Enum(EmploymentStatus), default=EmploymentStatus.ACTIVE)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    salary = Column(String, nullable=True)
    benefits = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
