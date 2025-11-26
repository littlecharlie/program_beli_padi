"""
Purchase Service
CRUD operations and business logic for purchase bills
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, text
from datetime import datetime
from decimal import Decimal
from models.purchase_bill import PurchaseBill
from services.calculation_service import CalculationService
from services.config_service import ConfigService


class PurchaseService:
    """Service for purchase bill operations"""

    @staticmethod
    def create(db: Session,
               farmer_id: int,
               truck_id: int,
               gross_weight: float,
               discount_wap_basah: float,
               discount_hampa_padi: float,
               discount_padi_muda: float,
               rice_price: float,
               subsidy_rate: float = 0.50,
               weighbridge_receipt: str = None,
               harvest_area_id: int = None,
               created_by: str = None) -> PurchaseBill:
        """
        Create new purchase bill with automatic calculations

        Args:
            db: Database session
            farmer_id: Farmer ID
            truck_id: Truck ID
            gross_weight: Gross weight in kg
            discount_wap_basah: Moisture discount %
            discount_hampa_padi: Empty grains discount %
            discount_padi_muda: Damaged rice discount %
            rice_price: Price per 1000kg
            subsidy_rate: Subsidy rate per kg
            weighbridge_receipt: Weighbridge receipt number
            harvest_area_id: Harvest area ID
            created_by: User who created the bill

        Returns:
            Created PurchaseBill object
        """
        # Get next bill number from database function
        try:
            bill_number = db.execute(
                text("SELECT get_next_bill_number()::text")
            ).scalar()

            if not bill_number:
                raise ValueError("Failed to generate bill number from database")
        except Exception as e:
            raise RuntimeError(f"Error getting next bill number: {str(e)}")

        # Calculate all values
        calcs = CalculationService.calculate_purchase_bill(
            gross_weight,
            discount_wap_basah,
            discount_hampa_padi,
            discount_padi_muda,
            rice_price,
            subsidy_rate
        )

        # Create purchase bill
        purchase_bill = PurchaseBill(
            bill_number=bill_number,
            farmer_id=farmer_id,
            truck_id=truck_id,
            gross_weight=Decimal(str(gross_weight)),
            discount_wap_basah=Decimal(str(discount_wap_basah)),
            discount_hampa_padi=Decimal(str(discount_hampa_padi)),
            discount_padi_muda=Decimal(str(discount_padi_muda)),
            total_discount_percent=Decimal(str(calcs['total_discount_percent'])),
            discount_weight=Decimal(str(calcs['discount_weight'])),
            net_weight=Decimal(str(calcs['net_weight'])),
            rice_price_per_1000kg=Decimal(str(rice_price)),
            total_payment=Decimal(str(calcs['total_payment'])),
            subsidy_estimate=Decimal(str(calcs['subsidy_estimate'])),
            weighbridge_receipt=weighbridge_receipt,
            harvest_area_id=harvest_area_id,
            created_by=created_by,
            bill_date=datetime.now()
        )

        db.add(purchase_bill)
        db.commit()
        db.refresh(purchase_bill)
        return purchase_bill

    @staticmethod
    def get_by_id(db: Session, bill_id: int) -> PurchaseBill:
        """Get purchase bill by ID"""
        return db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()

    @staticmethod
    def get_by_number(db: Session, bill_number: str) -> PurchaseBill:
        """Get purchase bill by bill number"""
        return db.query(PurchaseBill).filter(PurchaseBill.bill_number == bill_number).first()

    @staticmethod
    def get_all(db: Session, delivered_only: bool = False):
        """Get all purchase bills"""
        query = db.query(PurchaseBill)
        if delivered_only:
            query = query.filter(PurchaseBill.is_delivered == True)
        return query.order_by(desc(PurchaseBill.bill_date)).all()

    @staticmethod
    def get_undelivered(db: Session):
        """Get all undelivered purchase bills"""
        return db.query(PurchaseBill).filter(
            PurchaseBill.is_delivered == False
        ).order_by(desc(PurchaseBill.bill_date)).all()

    @staticmethod
    def get_by_farmer(db: Session, farmer_id: int, delivered_only: bool = False):
        """Get purchase bills by farmer"""
        query = db.query(PurchaseBill).filter(PurchaseBill.farmer_id == farmer_id)
        if delivered_only:
            query = query.filter(PurchaseBill.is_delivered == True)
        return query.order_by(desc(PurchaseBill.bill_date)).all()

    @staticmethod
    def get_by_date_range(db: Session, start_date: datetime, end_date: datetime,
                         delivered_only: bool = False):
        """Get purchase bills within date range"""
        query = db.query(PurchaseBill).filter(
            and_(
                PurchaseBill.bill_date >= start_date,
                PurchaseBill.bill_date <= end_date
            )
        )
        if delivered_only:
            query = query.filter(PurchaseBill.is_delivered == True)
        return query.order_by(desc(PurchaseBill.bill_date)).all()

    @staticmethod
    def search(db: Session, search_term: str, delivered_only: bool = False):
        """Search purchase bills by bill number or farmer name"""
        query = db.query(PurchaseBill).join(
            PurchaseBill.farmer_id == PurchaseBill.farmer_id
        )
        if delivered_only:
            query = query.filter(PurchaseBill.is_delivered == True)

        search_pattern = f"%{search_term}%"
        return query.filter(
            PurchaseBill.bill_number.ilike(search_pattern)
        ).order_by(desc(PurchaseBill.bill_date)).all()

    @staticmethod
    def update(db: Session, bill_id: int, **kwargs) -> PurchaseBill:
        """
        Update purchase bill
        Note: After a bill is printed, only certain fields can be updated
        """
        bill = PurchaseService.get_by_id(db, bill_id)
        if bill:
            # Fields that can be updated
            updatable_fields = [
                'discount_wap_basah',
                'discount_hampa_padi',
                'discount_padi_muda',
                'weighbridge_receipt',
                'harvest_area_id'
            ]

            for key, value in kwargs.items():
                if key in updatable_fields and value is not None:
                    setattr(bill, key, value)

            # Recalculate if any discount changed
            if any(k in kwargs for k in ['discount_wap_basah', 'discount_hampa_padi', 'discount_padi_muda']):
                calcs = CalculationService.calculate_purchase_bill(
                    float(bill.gross_weight),
                    float(bill.discount_wap_basah),
                    float(bill.discount_hampa_padi),
                    float(bill.discount_padi_muda),
                    float(bill.rice_price_per_1000kg)
                )
                bill.total_discount_percent = Decimal(str(calcs['total_discount_percent']))
                bill.discount_weight = Decimal(str(calcs['discount_weight']))
                bill.net_weight = Decimal(str(calcs['net_weight']))
                bill.total_payment = Decimal(str(calcs['total_payment']))
                bill.subsidy_estimate = Decimal(str(calcs['subsidy_estimate']))

            db.commit()
            db.refresh(bill)
        return bill

    @staticmethod
    def mark_as_delivered(db: Session, bill_id: int, delivery_invoice_id: int) -> PurchaseBill:
        """Mark purchase bill as delivered"""
        bill = PurchaseService.get_by_id(db, bill_id)
        if bill:
            bill.is_delivered = True
            bill.delivery_invoice_id = delivery_invoice_id
            db.commit()
            db.refresh(bill)
        return bill

    @staticmethod
    def delete(db: Session, bill_id: int) -> bool:
        """Delete purchase bill (only if not delivered)"""
        bill = PurchaseService.get_by_id(db, bill_id)
        if bill and not bill.is_delivered:
            db.delete(bill)
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session, delivered_only: bool = False) -> int:
        """Count purchase bills"""
        query = db.query(PurchaseBill)
        if delivered_only:
            query = query.filter(PurchaseBill.is_delivered == True)
        return query.count()

    @staticmethod
    def get_total_weight(db: Session, delivered_only: bool = False) -> float:
        """Get total net weight of all purchase bills"""
        query = db.query(PurchaseBill)
        if delivered_only:
            query = query.filter(PurchaseBill.is_delivered == True)

        bills = query.all()
        return CalculationService.calculate_delivery_total_weight(bills)

    @staticmethod
    def get_total_payment(db: Session, delivered_only: bool = False) -> float:
        """Get total payment of all purchase bills"""
        query = db.query(PurchaseBill)
        if delivered_only:
            query = query.filter(PurchaseBill.is_delivered == True)

        bills = query.all()
        total = Decimal('0')
        for bill in bills:
            total += Decimal(str(bill.total_payment))

        return float(total)

    @staticmethod
    def get_statistics(db: Session) -> dict:
        """Get purchase bill statistics"""
        all_bills = db.query(PurchaseBill).all()
        delivered_bills = db.query(PurchaseBill).filter(
            PurchaseBill.is_delivered == True
        ).all()

        return {
            'total_bills': len(all_bills),
            'delivered_bills': len(delivered_bills),
            'pending_bills': len(all_bills) - len(delivered_bills),
            'total_weight': CalculationService.calculate_delivery_total_weight(all_bills),
            'delivered_weight': CalculationService.calculate_delivery_total_weight(delivered_bills),
            'total_payment': PurchaseService.get_total_payment(db),
            'delivered_payment': PurchaseService.get_total_payment(db, delivered_only=True)
        }
