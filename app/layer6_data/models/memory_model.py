from sqlalchemy import Column, String, Text, DateTime, JSON, Index
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.layer6_data.models.base import Base

class MemoryModel(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False, index=True)  # e.g., "job", "candidate"
    title = Column(String, nullable=True)
    text = Column(Text, nullable=True)                 # canonical text for embedding
    embedding = Column(Vector(1536), nullable=True)    # OpenAI embedding size
    metadata_ = Column("metadata", JSON, nullable=True)
    canonical_json = Column(JSON, nullable=True)       # Full structured output
    short_id = Column(String, nullable=True, index=True) # e.g. tek0001
    user_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Note: IVFFlat index creation usually happens in migrations or raw SQL
    # as it requires specific parameters like 'lists'
