from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum

from app.layer6_data.models.base import Base


class ClientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    contact_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    status = Column(Enum(ClientStatus), default=ClientStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    jobs = relationship("JobModel", back_populates="client")
