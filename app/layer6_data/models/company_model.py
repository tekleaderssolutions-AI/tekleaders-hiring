from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.layer6_data.models.base import Base

class CompanySize(str, enum.Enum):
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"

class CompanyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class CompanyModel(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    industry = Column(String, nullable=True)
    size = Column(Enum(CompanySize), nullable=True)
    website = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    status = Column(Enum(CompanyStatus), default=CompanyStatus.ACTIVE)
    billing_info = Column(Text, nullable=True)          # JSON stored as text
    settings = Column(Text, nullable=True)              # JSON stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("UserModel", back_populates="company")
    jobs = relationship("JobModel", back_populates="company")
