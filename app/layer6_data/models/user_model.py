from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEWER = "interviewer"
    CANDIDATE = "candidate"

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.RECRUITER)
    google_id = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("CompanyModel", back_populates="users")
