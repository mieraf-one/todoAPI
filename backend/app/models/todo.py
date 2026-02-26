from sqlalchemy import Column, String, Integer, DateTime, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.utils.database import Base
from app.models import user


class Todo(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(String)
    is_done = Column(BOOLEAN, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))
    
    owner = relationship(
        'User',
        back_populates='todos'
    )