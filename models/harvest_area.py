"""
Harvest Area Model
Represents harvest area codes
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from models.base import Base


class HarvestArea(Base):
    """Harvest areas table"""
    __tablename__ = 'harvest_areas'

    id = Column(Integer, primary_key=True)
    area_name = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<HarvestArea(name='{self.area_name}')>"
