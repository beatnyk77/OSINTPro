from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.sql import func
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, index=True)
    summary = Column(Text)  # Summary of the content
    entities = Column(Text)  # JSON string of extracted entities
    source_type = Column(String(50))  # e.g., 'twitter', 'telegram', 'news'
    source_id = Column(String(255), index=True)  # the ID from the source
    credibility_score = Column(Float, default=0.0)  # Score between 0.0 and 1.0
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # We'll add more fields like geohash, etc. in Phase 2