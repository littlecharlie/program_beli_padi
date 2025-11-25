"""
Configuration Service
Manages system configuration stored in database
"""
from sqlalchemy.orm import Session
from models.config import Config


class ConfigService:
    """Service for managing configuration"""

    @staticmethod
    def get_value(db: Session, key: str, default=None):
        """Get configuration value by key"""
        config = db.query(Config).filter(Config.key == key).first()
        if config:
            return config.value
        return default

    @staticmethod
    def get_float_value(db: Session, key: str, default: float = 0.0) -> float:
        """Get configuration value as float"""
        value = ConfigService.get_value(db, key)
        if value:
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        return default

    @staticmethod
    def get_int_value(db: Session, key: str, default: int = 0) -> int:
        """Get configuration value as integer"""
        value = ConfigService.get_value(db, key)
        if value:
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        return default

    @staticmethod
    def set_value(db: Session, key: str, value: str, description: str = None):
        """Set configuration value"""
        config = db.query(Config).filter(Config.key == key).first()
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = Config(key=key, value=value, description=description)
            db.add(config)
        db.commit()
        return config

    @staticmethod
    def get_all(db: Session):
        """Get all configuration items"""
        return db.query(Config).all()

    @staticmethod
    def delete(db: Session, key: str):
        """Delete configuration by key"""
        config = db.query(Config).filter(Config.key == key).first()
        if config:
            db.delete(config)
            db.commit()
            return True
        return False
