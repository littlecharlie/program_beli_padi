"""
First Run Setup Script
Runs after installation to verify configuration and database setup
"""
import os
import sys
from pathlib import Path

def check_environment():
    """Check if .env file exists and is configured"""
    print("Checking environment configuration...")

    env_file = Path(".env")
    if not env_file.exists():
        print("❌ ERROR: .env file not found!")
        print("   The installer should have created this file.")
        return False

    # Read .env file
    with open(env_file, 'r') as f:
        env_content = f.read()

    # Check for demo mode
    if "DEMO_MODE=true" in env_content:
        print("✓ Configuration: DEMO MODE")
        print("  Application will run without database")
        return True

    # Check database configuration
    print("✓ Configuration: DATABASE MODE")

    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER']
    missing_vars = []

    for var in required_vars:
        if f"{var}=" not in env_content:
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ ERROR: Missing configuration: {', '.join(missing_vars)}")
        return False

    print("✓ Database configuration found")
    return True

def check_database_connection():
    """Test database connection if not in demo mode"""
    print("\nChecking database connection...")

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'

    if demo_mode:
        print("⊘ Skipped (Demo mode)")
        return True

    # Try to connect to database
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.close()
        print("✓ Database connection successful!")
        return True

    except ImportError:
        print("❌ ERROR: psycopg2 not installed")
        print("   This should not happen in a proper installation")
        return False

    except Exception as e:
        print(f"❌ ERROR: Cannot connect to database")
        print(f"   {str(e)}")
        print("\n   Please check:")
        print("   1. PostgreSQL service is running")
        print("   2. Database exists")
        print("   3. Credentials in .env file are correct")
        print("\n   You can:")
        print("   - Edit .env file to fix database settings")
        print("   - OR set DEMO_MODE=true to run without database")
        return False

def check_directories():
    """Create necessary directories"""
    print("\nChecking application directories...")

    directories = ['exports', 'backups', 'logs']

    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {dir_name}/")
        else:
            print(f"✓ Exists: {dir_name}/")

    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("RICE BILLING SYSTEM - FIRST RUN SETUP")
    print("=" * 60)
    print()

    # Change to application directory
    app_dir = Path(__file__).parent.parent
    os.chdir(app_dir)

    success = True

    # Run checks
    if not check_environment():
        success = False

    if not check_directories():
        success = False

    # Try database connection (will be skipped if demo mode)
    if not check_database_connection():
        success = False

    print()
    print("=" * 60)

    if success:
        print("✓ SETUP COMPLETE")
        print()
        print("Your Rice Billing System is ready to use!")
        print()
        print("Next steps:")
        print("1. Launch the application from the desktop shortcut")
        print("2. Configure company details in Settings")
        print("3. Add farmers, mills, trucks in Master Data")
        print("4. Start creating purchase bills!")
    else:
        print("⚠ SETUP COMPLETED WITH WARNINGS")
        print()
        print("The application may not work correctly.")
        print("Please review the errors above and:")
        print("1. Fix database configuration in .env file")
        print("2. OR run in demo mode (set DEMO_MODE=true)")
        print()
        print("After fixing, you can run this setup again")

    print("=" * 60)
    print()
    input("Press Enter to close...")

    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ ERROR: Setup failed with exception:")
        print(f"   {str(e)}")
        print()
        input("Press Enter to close...")
        sys.exit(1)
