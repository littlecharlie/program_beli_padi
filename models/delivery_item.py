"""
Delivery Item Model
Junction table linking purchase bills to delivery invoices
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from models.base import Base


class DeliveryItem(Base):
    """Delivery items junction table"""
    __tablename__ = 'delivery_items'

    id = Column(Integer, primary_key=True)
    delivery_invoice_id = Column(Integer, ForeignKey('delivery_invoices.id', ondelete='CASCADE'), nullable=False)
    purchase_bill_id = Column(Integer, ForeignKey('purchase_bills.id', ondelete='RESTRICT'), nullable=False)

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('delivery_invoice_id', 'purchase_bill_id', name='uq_delivery_purchase'),
    )

    def __repr__(self):
        return f"<DeliveryItem(delivery_id={self.delivery_invoice_id}, bill_id={self.purchase_bill_id})>"
