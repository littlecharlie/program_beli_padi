"""
Rice Billing System
Main application entry point
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox

# Check if running in demo mode
DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'

if not DEMO_MODE:
    from database.connection import DatabaseManager

from ui.main_window import MainWindow


def main():
    """Main entry point"""
    if DEMO_MODE:
        print("Running in DEMO MODE - no database required")
    else:
        # Test database connection
        print("Connecting to database...")
        if not DatabaseManager.test_connection():
            print("ERROR: Cannot connect to database")
            print("TIP: Set DEMO_MODE=true in .env to run without database")
            sys.exit(1)

        # Initialize database tables
        print("Initializing database...")
        DatabaseManager.init_db()

    # Create Qt application
    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow(demo_mode=DEMO_MODE)
    window.show()

    if DEMO_MODE:
        QMessageBox.information(
            window,
            "Demo Mode",
            "Running in DEMO MODE\n\nDatabase is not connected.\n"
            "UI elements are functional for testing.\n\n"
            "To use with real database:\n"
            "1. Install PostgreSQL\n"
            "2. Set DEMO_MODE=false in .env\n"
            "3. Restart the application"
        )

    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
