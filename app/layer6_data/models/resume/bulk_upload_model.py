from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean
from app.database import Base
from datetime import datetime

class BulkUploadModel(Base):
    __tablename__ = "bulk_uploads"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    total_files = Column(Integer, default=0)
    unique_files = Column(Integer, default=0)
    duplicate_files = Column(Integer, default=0)
    processed_count = Column(Integer, default=0)
    status = Column(String, default="processing") # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
