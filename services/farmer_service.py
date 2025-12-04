"""
Farmer Service
CRUD operations for farmers
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.farmer import Farmer


class FarmerService:
    """Service for farmer operations"""

    @staticmethod
    def create(db: Session, ic_number: str, name: str, address: str = None,
               phone: str = None, registration_number: str = None,
               subsidy_code: str = None, bank_account: str = None) -> Farmer:
        """Create new farmer"""
        farmer = Farmer(
            ic_number=ic_number,
            name=name,
            address=address,
            phone=phone,
            registration_number=registration_number,
            subsidy_code=subsidy_code,
            bank_account=bank_account
        )
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
        return farmer

    @staticmethod
    def get_by_id(db: Session, farmer_id: int) -> Farmer:
        """Get farmer by ID"""
        return db.query(Farmer).filter(Farmer.id == farmer_id).first()

    @staticmethod
    def get_by_ic(db: Session, ic_number: str) -> Farmer:
        """Get farmer by IC number"""
        return db.query(Farmer).filter(Farmer.ic_number == ic_number).first()

    @staticmethod
    def get_all(db: Session, active_only: bool = True):
        """Get all farmers"""
        query = db.query(Farmer)
        if active_only:
            query = query.filter(Farmer.is_active == True)
        return query.order_by(Farmer.name).all()

    @staticmethod
    def search(db: Session, search_term: str, active_only: bool = True):
        """Search farmers by IC or name"""
        query = db.query(Farmer)
        if active_only:
            query = query.filter(Farmer.is_active == True)

        search_pattern = f"%{search_term}%"
        return query.filter(
            (Farmer.ic_number.ilike(search_pattern)) |
            (Farmer.name.ilike(search_pattern))
        ).order_by(Farmer.name).all()

    @staticmethod
    def update(db: Session, farmer_id: int, **kwargs) -> Farmer:
        """Update farmer"""
        farmer = FarmerService.get_by_id(db, farmer_id)
        if farmer:
            for key, value in kwargs.items():
                if hasattr(farmer, key) and value is not None:
                    setattr(farmer, key, value)
            db.commit()
            db.refresh(farmer)
        return farmer

    @staticmethod
    def delete(db: Session, farmer_id: int) -> bool:
        """Soft delete farmer (set is_active to False)"""
        farmer = FarmerService.get_by_id(db, farmer_id)
        if farmer:
            farmer.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def reactivate(db: Session, farmer_id: int) -> bool:
        """Reactivate farmer (set is_active to True)"""
        farmer = FarmerService.get_by_id(db, farmer_id)
        if farmer:
            farmer.is_active = True
            db.commit()
            return True
        return False

    @staticmethod
    def hard_delete(db: Session, farmer_id: int) -> bool:
        """Permanently delete farmer"""
        farmer = FarmerService.get_by_id(db, farmer_id)
        if farmer:
            db.delete(farmer)
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session, active_only: bool = True) -> int:
        """Count farmers"""
        query = db.query(Farmer)
        if active_only:
            query = query.filter(Farmer.is_active == True)
        return query.count()
