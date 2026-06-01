from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.layer6_data.models.base import Base


class JDAssignmentModel(Base):
    __tablename__ = "jd_assignments"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    employee_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    assigned_by = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("job_id", "employee_id", name="_jd_employee_uc"),)

    # Relationships
    job = relationship("JobModel", back_populates="assignments")
    employee = relationship("UserModel", foreign_keys=[employee_id])
    assigner = relationship("UserModel", foreign_keys=[assigned_by])
