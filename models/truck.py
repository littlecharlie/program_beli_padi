"""
Truck Model
Represents trucks used for transport
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from models.base import Base


class Truck(Base):
    """Trucks table"""
    __tablename__ = 'trucks'

    id = Column(Integer, primary_key=True)
    truck_number = Column(String(20), unique=True, nullable=False, index=True)
    tare_weight = Column(Numeric(10, 2))  # Optional tare weight
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Truck(number='{self.truck_number}')>"
