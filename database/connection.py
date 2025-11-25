"""
Database Connection Manager
Handles database connection, initialization, and cleanup
"""
import os
from sqlalchemy import text
from config.database import engine, SessionLocal, get_db
from models import Base


class DatabaseManager:
    """Manage database connections and initialization"""

    @staticmethod
    def init_db():
        """Initialize database tables"""
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")

    @staticmethod
    def drop_all():
        """Drop all tables (for development/testing)"""
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped")

    @staticmethod
    def execute_sql_file(filepath):
        """Execute SQL file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"SQL file not found: {filepath}")

        with open(filepath, 'r') as f:
            sql_content = f.read()

        db = SessionLocal()
        try:
            # Split by semicolon and execute each statement
            statements = sql_content.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    db.execute(text(statement))
            db.commit()
            print(f"SQL file executed successfully: {filepath}")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def test_connection():
        """Test database connection"""
        try:
            db = SessionLocal()
            result = db.execute(text("SELECT 1"))
            db.close()
            print("Database connection successful")
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

    @staticmethod
    def close():
        """Close database connection"""
        engine.dispose()
        print("Database connection closed")
