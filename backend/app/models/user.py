from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship

from app.utils.database import Base
from app.models import todo

from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    username = Column(String, nullable=False, unique=True, name='uq_users_username')
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    todos = relationship(
        'Todo', 
        back_populates='owner',
        cascade='all, delete'
    )