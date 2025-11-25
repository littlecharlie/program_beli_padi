"""
Delivery Service
CRUD operations for delivery invoices and items
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime
from decimal import Decimal
from models.delivery_invoice import DeliveryInvoice
from models.delivery_item import DeliveryItem
from models.purchase_bill import PurchaseBill
from services.calculation_service import CalculationService
from services.purchase_service import PurchaseService


class DeliveryService:
    """Service for delivery invoice operations"""

    @staticmethod
    def create(db: Session,
               mill_id: int,
               truck_id: int,
               purchase_bill_ids: list,
               created_by: str = None) -> DeliveryInvoice:
        """
        Create new delivery invoice with selected purchase bills

        Args:
            db: Database session
            mill_id: Rice mill ID
            truck_id: Truck ID
            purchase_bill_ids: List of purchase bill IDs to include
            created_by: User who created the invoice

        Returns:
            Created DeliveryInvoice object
        """
        if not purchase_bill_ids:
            raise ValueError("At least one purchase bill must be selected")

        # Get all selected bills
        bills = db.query(PurchaseBill).filter(
            PurchaseBill.id.in_(purchase_bill_ids)
        ).all()

        if not bills:
            raise ValueError("No valid purchase bills found")

        # Validate bills (must not be delivered, must be for same mill)
        for bill in bills:
            if bill.is_delivered:
                raise ValueError(f"Bill {bill.bill_number} is already delivered")

        # Calculate total weight
        total_weight = CalculationService.calculate_delivery_total_weight(bills)

        # Get next invoice number from database function
        invoice_number = db.execute(
            "SELECT get_next_invoice_number()"
        ).scalar()

        # Create delivery invoice
        delivery_invoice = DeliveryInvoice(
            invoice_number=invoice_number,
            mill_id=mill_id,
            truck_id=truck_id,
            total_weight=Decimal(str(total_weight)),
            created_by=created_by,
            invoice_date=datetime.now()
        )

        db.add(delivery_invoice)
        db.flush()  # Flush to get the ID

        # Create delivery items
        for bill in bills:
            delivery_item = DeliveryItem(
                delivery_invoice_id=delivery_invoice.id,
                purchase_bill_id=bill.id
            )
            db.add(delivery_item)

            # Mark bill as delivered
            bill.is_delivered = True
            bill.delivery_invoice_id = delivery_invoice.id

        db.commit()
        db.refresh(delivery_invoice)
        return delivery_invoice

    @staticmethod
    def get_by_id(db: Session, invoice_id: int) -> DeliveryInvoice:
        """Get delivery invoice by ID"""
        return db.query(DeliveryInvoice).filter(
            DeliveryInvoice.id == invoice_id
        ).first()

    @staticmethod
    def get_by_number(db: Session, invoice_number: str) -> DeliveryInvoice:
        """Get delivery invoice by invoice number"""
        return db.query(DeliveryInvoice).filter(
            DeliveryInvoice.invoice_number == invoice_number
        ).first()

    @staticmethod
    def get_all(db: Session):
        """Get all delivery invoices"""
        return db.query(DeliveryInvoice).order_by(
            desc(DeliveryInvoice.invoice_date)
        ).all()

    @staticmethod
    def get_by_mill(db: Session, mill_id: int):
        """Get delivery invoices by mill"""
        return db.query(DeliveryInvoice).filter(
            DeliveryInvoice.mill_id == mill_id
        ).order_by(desc(DeliveryInvoice.invoice_date)).all()

    @staticmethod
    def get_by_date_range(db: Session, start_date: datetime, end_date: datetime):
        """Get delivery invoices within date range"""
        return db.query(DeliveryInvoice).filter(
            and_(
                DeliveryInvoice.invoice_date >= start_date,
                DeliveryInvoice.invoice_date <= end_date
            )
        ).order_by(desc(DeliveryInvoice.invoice_date)).all()

    @staticmethod
    def search(db: Session, search_term: str):
        """Search delivery invoices by invoice number"""
        search_pattern = f"%{search_term}%"
        return db.query(DeliveryInvoice).filter(
            DeliveryInvoice.invoice_number.ilike(search_pattern)
        ).order_by(desc(DeliveryInvoice.invoice_date)).all()

    @staticmethod
    def get_items(db: Session, invoice_id: int):
        """Get all delivery items (purchase bills) for an invoice"""
        return db.query(DeliveryItem).filter(
            DeliveryItem.delivery_invoice_id == invoice_id
        ).all()

    @staticmethod
    def get_bills_for_invoice(db: Session, invoice_id: int):
        """Get all purchase bills for an invoice with full details"""
        items = DeliveryService.get_items(db, invoice_id)
        bill_ids = [item.purchase_bill_id for item in items]

        if not bill_ids:
            return []

        return db.query(PurchaseBill).filter(
            PurchaseBill.id.in_(bill_ids)
        ).all()

    @staticmethod
    def update(db: Session, invoice_id: int, **kwargs) -> DeliveryInvoice:
        """Update delivery invoice (limited fields)"""
        invoice = DeliveryService.get_by_id(db, invoice_id)
        if invoice:
            # Only certain fields can be updated
            updatable_fields = []

            for key, value in kwargs.items():
                if key in updatable_fields and value is not None:
                    setattr(invoice, key, value)

            db.commit()
            db.refresh(invoice)

        return invoice

    @staticmethod
    def delete(db: Session, invoice_id: int) -> bool:
        """Delete delivery invoice and unmark bills as delivered"""
        invoice = DeliveryService.get_by_id(db, invoice_id)
        if invoice:
            # Get all bills for this invoice
            items = DeliveryService.get_items(db, invoice_id)

            # Unmark bills as delivered
            for item in items:
                bill = PurchaseService.get_by_id(db, item.purchase_bill_id)
                if bill:
                    bill.is_delivered = False
                    bill.delivery_invoice_id = None

            # Delete delivery items
            for item in items:
                db.delete(item)

            # Delete invoice
            db.delete(invoice)
            db.commit()
            return True

        return False

    @staticmethod
    def count(db: Session) -> int:
        """Count delivery invoices"""
        return db.query(DeliveryInvoice).count()

    @staticmethod
    def get_total_weight(db: Session) -> float:
        """Get total weight of all delivery invoices"""
        invoices = db.query(DeliveryInvoice).all()
        total = Decimal('0')
        for invoice in invoices:
            total += Decimal(str(invoice.total_weight))
        return float(total)

    @staticmethod
    def get_statistics(db: Session) -> dict:
        """Get delivery invoice statistics"""
        invoices = db.query(DeliveryInvoice).all()
        items = db.query(DeliveryItem).all()

        return {
            'total_invoices': len(invoices),
            'total_bills_delivered': len(items),
            'total_weight': DeliveryService.get_total_weight(db),
            'avg_invoice_weight': (
                sum(float(i.total_weight) for i in invoices) / len(invoices)
                if invoices else 0
            )
        }
