"""
Database Configuration
Centralized database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import DatabaseConfig

# Create database engine
engine = create_engine(
    DatabaseConfig.get_connection_string(),
    echo=False,  # Set to True for SQL logging
    future=True
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)


def get_db() -> Session:
    """
    Get a database session
    For use in services and dependencies
    """
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def close_db():
    """Close database connection"""
    engine.dispose()
