"""
Audit Log Model
Tracks all changes to critical tables
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from models.base import Base


class AuditLog(Base):
    """Audit log table for tracking changes"""
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer)
    action = Column(String(20), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(JSON)
    new_values = Column(JSON)
    user_name = Column(String(100))
    created_at = Column(DateTime, default=func.now(), index=True)

    def __repr__(self):
        return f"<AuditLog(table='{self.table_name}', action='{self.action}', record_id={self.record_id})>"
