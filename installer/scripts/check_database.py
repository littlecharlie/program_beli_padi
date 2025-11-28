"""
Database Connection Checker
Quick script to test database connectivity
"""
import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("DATABASE CONNECTION CHECKER")
    print("=" * 60)
    print()

    # Load environment
    try:
        from dotenv import load_dotenv
        env_file = Path(".env")

        if not env_file.exists():
            print("❌ ERROR: .env file not found!")
            print("   Run the application first to create configuration.")
            input("\nPress Enter to exit...")
            return 1

        load_dotenv()
    except ImportError:
        print("❌ ERROR: python-dotenv not installed")
        input("\nPress Enter to exit...")
        return 1

    # Check demo mode
    demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'

    if demo_mode:
        print("ℹ Application is in DEMO MODE")
        print("  No database connection required")
        print()
        input("Press Enter to exit...")
        return 0

    # Get database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'rice_billing_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }

    print("Database Configuration:")
    print(f"  Host: {db_config['host']}")
    print(f"  Port: {db_config['port']}")
    print(f"  Database: {db_config['database']}")
    print(f"  User: {db_config['user']}")
    print(f"  Password: {'*' * len(db_config['password']) if db_config['password'] else '(not set)'}")
    print()

    # Try to connect
    print("Testing connection...")

    try:
        import psycopg2

        conn = psycopg2.connect(**db_config)

        # Get database version
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()[0]

        # Get table count
        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        table_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        print("✓ CONNECTION SUCCESSFUL!")
        print()
        print(f"PostgreSQL Version:")
        print(f"  {db_version.split(',')[0]}")
        print()
        print(f"Database Tables: {table_count}")
        print()

        if table_count == 0:
            print("⚠ WARNING: No tables found in database")
            print("  The application will create tables on first run")
        else:
            print("✓ Database appears to be initialized")

        print()
        print("Your database connection is working correctly!")

    except ImportError:
        print("❌ ERROR: psycopg2 module not found")
        print("   This should not happen in a packaged application")

    except psycopg2.OperationalError as e:
        print("❌ CONNECTION FAILED")
        print()
        print(f"Error: {str(e)}")
        print()
        print("Common causes:")
        print("  1. PostgreSQL service not running")
        print("     → Start PostgreSQL service")
        print()
        print("  2. Wrong database name")
        print("     → Create database: CREATE DATABASE rice_billing_db;")
        print()
        print("  3. Wrong credentials")
        print("     → Check username/password in .env file")
        print()
        print("  4. Firewall blocking connection")
        print("     → Check firewall settings")
        print()
        print("Solution:")
        print("  Edit the .env file in the application folder")
        print("  Or run in demo mode (set DEMO_MODE=true)")

    except Exception as e:
        print("❌ UNEXPECTED ERROR")
        print(f"   {str(e)}")

    print()
    print("=" * 60)
    input("\nPress Enter to exit...")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
