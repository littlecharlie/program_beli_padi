"""
Farmer Model
Represents farmers/suppliers
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from models.base import Base


class Farmer(Base):
    """Farmers/suppliers table"""
    __tablename__ = 'farmers'

    id = Column(Integer, primary_key=True)
    ic_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    address = Column(Text)
    phone = Column(String(20))
    registration_number = Column(String(50))  # NO DAFTAR PESAWAH
    subsidy_code = Column(String(50))  # NO KAD SUBSIDI
    bank_account = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Farmer(ic='{self.ic_number}', name='{self.name}')>"
