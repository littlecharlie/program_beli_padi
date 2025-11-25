"""
Delivery Invoice Model
Represents consolidated delivery invoices
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class DeliveryInvoice(Base):
    """Delivery invoices (INVOIS HANTARAN) table"""
    __tablename__ = 'delivery_invoices'

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(20), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime, default=func.now(), nullable=False)

    mill_id = Column(Integer, ForeignKey('rice_mills.id', ondelete='RESTRICT'), nullable=False)
    truck_id = Column(Integer, ForeignKey('trucks.id', ondelete='RESTRICT'), nullable=False)

    total_weight = Column(Numeric(10, 2), nullable=False)

    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(100))

    def __repr__(self):
        return f"<DeliveryInvoice(number='{self.invoice_number}', total_weight={self.total_weight})>"
