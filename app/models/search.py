from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.db.database import Base
from datetime import datetime

class SearchJob(Base):
    __tablename__ = "search_jobs"
    id = Column(String, primary_key=True, index=True)
    query = Column(String)
    status = Column(String, default="pending")
    state = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)