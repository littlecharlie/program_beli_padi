"""
Rice Mill Service
CRUD operations for rice mills
"""
from sqlalchemy.orm import Session
from models.rice_mill import RiceMill


class RiceMillService:
    """Service for rice mill operations"""

    @staticmethod
    def create(db: Session, mill_code: str, mill_name: str, address: str = None,
               phone: str = None) -> RiceMill:
        """Create new rice mill"""
        mill = RiceMill(
            mill_code=mill_code,
            mill_name=mill_name,
            address=address,
            phone=phone
        )
        db.add(mill)
        db.commit()
        db.refresh(mill)
        return mill

    @staticmethod
    def get_by_id(db: Session, mill_id: int) -> RiceMill:
        """Get rice mill by ID"""
        return db.query(RiceMill).filter(RiceMill.id == mill_id).first()

    @staticmethod
    def get_by_code(db: Session, mill_code: str) -> RiceMill:
        """Get rice mill by code"""
        return db.query(RiceMill).filter(RiceMill.mill_code == mill_code).first()

    @staticmethod
    def get_all(db: Session, active_only: bool = True):
        """Get all rice mills"""
        query = db.query(RiceMill)
        if active_only:
            query = query.filter(RiceMill.is_active == True)
        return query.order_by(RiceMill.mill_name).all()

    @staticmethod
    def search(db: Session, search_term: str, active_only: bool = True):
        """Search rice mills by code or name"""
        query = db.query(RiceMill)
        if active_only:
            query = query.filter(RiceMill.is_active == True)

        search_pattern = f"%{search_term}%"
        return query.filter(
            (RiceMill.mill_code.ilike(search_pattern)) |
            (RiceMill.mill_name.ilike(search_pattern))
        ).order_by(RiceMill.mill_name).all()

    @staticmethod
    def update(db: Session, mill_id: int, **kwargs) -> RiceMill:
        """Update rice mill"""
        mill = RiceMillService.get_by_id(db, mill_id)
        if mill:
            for key, value in kwargs.items():
                if hasattr(mill, key) and value is not None:
                    setattr(mill, key, value)
            db.commit()
            db.refresh(mill)
        return mill

    @staticmethod
    def delete(db: Session, mill_id: int) -> bool:
        """Soft delete rice mill (set is_active to False)"""
        mill = RiceMillService.get_by_id(db, mill_id)
        if mill:
            mill.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session, active_only: bool = True) -> int:
        """Count rice mills"""
        query = db.query(RiceMill)
        if active_only:
            query = query.filter(RiceMill.is_active == True)
        return query.count()
