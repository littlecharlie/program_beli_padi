"""
Truck Service
CRUD operations for trucks
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from models.truck import Truck


class TruckService:
    """Service for truck operations"""

    @staticmethod
    def create(db: Session, truck_number: str, tare_weight: float = None) -> Truck:
        """Create new truck"""
        truck = Truck(
            truck_number=truck_number,
            tare_weight=Decimal(str(tare_weight)) if tare_weight else None
        )
        db.add(truck)
        db.commit()
        db.refresh(truck)
        return truck

    @staticmethod
    def get_by_id(db: Session, truck_id: int) -> Truck:
        """Get truck by ID"""
        return db.query(Truck).filter(Truck.id == truck_id).first()

    @staticmethod
    def get_by_number(db: Session, truck_number: str) -> Truck:
        """Get truck by number"""
        return db.query(Truck).filter(Truck.truck_number == truck_number).first()

    @staticmethod
    def get_all(db: Session, active_only: bool = True):
        """Get all trucks"""
        query = db.query(Truck)
        if active_only:
            query = query.filter(Truck.is_active == True)
        return query.order_by(Truck.truck_number).all()

    @staticmethod
    def search(db: Session, search_term: str, active_only: bool = True):
        """Search trucks by number"""
        query = db.query(Truck)
        if active_only:
            query = query.filter(Truck.is_active == True)

        search_pattern = f"%{search_term}%"
        return query.filter(Truck.truck_number.ilike(search_pattern)).order_by(Truck.truck_number).all()

    @staticmethod
    def update(db: Session, truck_id: int, **kwargs) -> Truck:
        """Update truck"""
        truck = TruckService.get_by_id(db, truck_id)
        if truck:
            for key, value in kwargs.items():
                if hasattr(truck, key) and value is not None:
                    if key == 'tare_weight':
                        setattr(truck, key, Decimal(str(value)))
                    else:
                        setattr(truck, key, value)
            db.commit()
            db.refresh(truck)
        return truck

    @staticmethod
    def delete(db: Session, truck_id: int) -> bool:
        """Soft delete truck (set is_active to False)"""
        truck = TruckService.get_by_id(db, truck_id)
        if truck:
            truck.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session, active_only: bool = True) -> int:
        """Count trucks"""
        query = db.query(Truck)
        if active_only:
            query = query.filter(Truck.is_active == True)
        return query.count()
