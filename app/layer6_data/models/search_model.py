from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, func
from pgvector.sqlalchemy import Vector
from app.layer6_data.models.base import Base

class SearchSessionModel(Base):
    """
    SEARCH / INTENT LAYER
    Captures recruiter search intent and semantic queries.
    Used for analytics and improving matching accuracy.
    """
    __tablename__ = "search_sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    
    query_text = Column(String, nullable=True)
    query_embedding = Column(Vector(1536), nullable=True) # The vector used for the search
    
    filters_json = Column(JSON, nullable=True)           # The structured filters applied
    results_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
