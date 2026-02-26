from app.utils.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from datetime import datetime, timezone

class Token(Base):
    __tablename__ = 'tokens'
    
    id = Column(Integer, primary_key=True)
    token = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))