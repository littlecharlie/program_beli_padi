"""
Purchase Bill Model
Represents individual rice purchase transactions
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class PurchaseBill(Base):
    """Purchase bills (BIL BELIAN PADI) table"""
    __tablename__ = 'purchase_bills'

    id = Column(Integer, primary_key=True)
    bill_number = Column(String(20), unique=True, nullable=False, index=True)
    farmer_id = Column(Integer, ForeignKey('farmers.id', ondelete='RESTRICT'), nullable=False)
    bill_date = Column(DateTime, default=func.now(), nullable=False)

    # Weighing information
    truck_id = Column(Integer, ForeignKey('trucks.id', ondelete='RESTRICT'))
    weighbridge_receipt = Column(String(50))
    gross_weight = Column(Numeric(10, 2), nullable=False)

    # Discount percentages
    discount_wap_basah = Column(Numeric(5, 2), default=7.00)
    discount_hampa_padi = Column(Numeric(5, 2), default=7.00)
    discount_padi_muda = Column(Numeric(5, 2), default=6.00)
    total_discount_percent = Column(Numeric(5, 2), nullable=False)

    # Calculated weights
    discount_weight = Column(Numeric(10, 2), nullable=False)
    net_weight = Column(Numeric(10, 2), nullable=False)

    # Payment calculations
    rice_price_per_1000kg = Column(Numeric(10, 2), nullable=False)
    total_payment = Column(Numeric(10, 2), nullable=False)
    subsidy_estimate = Column(Numeric(10, 2), nullable=False)

    # Additional information
    harvest_area_id = Column(Integer, ForeignKey('harvest_areas.id', ondelete='SET NULL'))

    # Status tracking
    is_delivered = Column(Boolean, default=False, index=True)
    delivery_invoice_id = Column(Integer, ForeignKey('delivery_invoices.id', ondelete='SET NULL'))

    # Audit fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(100))

    def __repr__(self):
        return f"<PurchaseBill(number='{self.bill_number}', net_weight={self.net_weight})>"
