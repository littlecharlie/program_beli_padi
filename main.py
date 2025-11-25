"""
Rice Billing System
Main application entry point
"""
import sys
from PyQt6.QtWidgets import QApplication
from database.connection import DatabaseManager
from ui.main_window import MainWindow


def main():
    """Main entry point"""
    # Test database connection
    print("Connecting to database...")
    if not DatabaseManager.test_connection():
        print("ERROR: Cannot connect to database")
        sys.exit(1)

    # Initialize database tables
    print("Initializing database...")
    DatabaseManager.init_db()

    # Create Qt application
    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
