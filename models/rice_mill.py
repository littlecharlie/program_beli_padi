"""
Rice Mill Model
Represents rice mills (destinations for delivery)
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from models.base import Base


class RiceMill(Base):
    """Rice mills table"""
    __tablename__ = 'rice_mills'

    id = Column(Integer, primary_key=True)
    mill_code = Column(String(10), unique=True, nullable=False, index=True)
    mill_name = Column(String(200), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<RiceMill(code='{self.mill_code}', name='{self.mill_name}')>"
