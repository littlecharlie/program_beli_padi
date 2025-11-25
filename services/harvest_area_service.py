"""
Harvest Area Service
CRUD operations for harvest areas
"""
from sqlalchemy.orm import Session
from models.harvest_area import HarvestArea


class HarvestAreaService:
    """Service for harvest area operations"""

    @staticmethod
    def create(db: Session, area_name: str) -> HarvestArea:
        """Create new harvest area"""
        area = HarvestArea(area_name=area_name)
        db.add(area)
        db.commit()
        db.refresh(area)
        return area

    @staticmethod
    def get_by_id(db: Session, area_id: int) -> HarvestArea:
        """Get harvest area by ID"""
        return db.query(HarvestArea).filter(HarvestArea.id == area_id).first()

    @staticmethod
    def get_by_name(db: Session, area_name: str) -> HarvestArea:
        """Get harvest area by name"""
        return db.query(HarvestArea).filter(HarvestArea.area_name == area_name).first()

    @staticmethod
    def get_all(db: Session, active_only: bool = True):
        """Get all harvest areas"""
        query = db.query(HarvestArea)
        if active_only:
            query = query.filter(HarvestArea.is_active == True)
        return query.order_by(HarvestArea.area_name).all()

    @staticmethod
    def search(db: Session, search_term: str, active_only: bool = True):
        """Search harvest areas by name"""
        query = db.query(HarvestArea)
        if active_only:
            query = query.filter(HarvestArea.is_active == True)

        search_pattern = f"%{search_term}%"
        return query.filter(HarvestArea.area_name.ilike(search_pattern)).order_by(HarvestArea.area_name).all()

    @staticmethod
    def update(db: Session, area_id: int, **kwargs) -> HarvestArea:
        """Update harvest area"""
        area = HarvestAreaService.get_by_id(db, area_id)
        if area:
            for key, value in kwargs.items():
                if hasattr(area, key) and value is not None:
                    setattr(area, key, value)
            db.commit()
            db.refresh(area)
        return area

    @staticmethod
    def delete(db: Session, area_id: int) -> bool:
        """Soft delete harvest area (set is_active to False)"""
        area = HarvestAreaService.get_by_id(db, area_id)
        if area:
            area.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session, active_only: bool = True) -> int:
        """Count harvest areas"""
        query = db.query(HarvestArea)
        if active_only:
            query = query.filter(HarvestArea.is_active == True)
        return query.count()
