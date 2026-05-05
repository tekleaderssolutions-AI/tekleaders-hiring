from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.layer6_data.models.base import Base

class AgentRunModel(Base):
    """
    AGENT WORKFLOW LAYER
    Tracks the execution of multi-step agentic workflows.
    """
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=True, index=True)
    
    workflow_name = Column(String, nullable=False) # e.g. "resume_ingestion", "candidate_matching"
    status = Column(String, default="pending")      # pending, running, completed, failed
    
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    steps = relationship("AgentStepModel", back_populates="run", cascade="all, delete-orphan")

class AgentStepModel(Base):
    """
    Individual steps within an agentic run.
    """
    __tablename__ = "agent_steps"

    id = Column(String, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("agent_runs.id"), nullable=False, index=True)
    
    step_name = Column(String, nullable=False) # e.g. "pii_redaction", "skill_extraction"
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    
    status = Column(String, default="completed")
    latency_ms = Column(Float := 0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    run = relationship("AgentRunModel", back_populates="steps")
