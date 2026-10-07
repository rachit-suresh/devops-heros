from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class Album(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(200), nullable=False)
    year = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 once listened
    status = Column(String(20), nullable=False, default="queued")  # queued | listening | listened
    created_at = Column(DateTime, server_default=func.now())
