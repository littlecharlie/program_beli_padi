#!/usr/bin/env python3
"""
Migration Runner
Executes database migration scripts safely
"""
import os
import sys
from pathlib import Path
from sqlalchemy import text
from config.database import SessionLocal


def run_migration(migration_file: str):
    """
    Execute a migration SQL file

    Args:
        migration_file: Path to SQL migration file
    """
    migration_path = Path(migration_file)

    if not migration_path.exists():
        print(f"Error: Migration file not found: {migration_path}")
        return False

    print(f"Running migration: {migration_path.name}")
    print(f"Path: {migration_path.absolute()}")
    print("-" * 60)

    with open(migration_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    db = SessionLocal()
    try:
        # Use raw connection to execute multi-statement SQL
        connection = db.connection()
        cursor = connection.connection.cursor()

        # Execute the entire SQL file
        cursor.execute(sql_content)
        connection.connection.commit()

        print("-" * 60)
        print(f"Migration completed successfully: {migration_path.name}")
        return True

    except Exception as e:
        try:
            db.rollback()
        except:
            pass
        print("-" * 60)
        print(f"Migration failed: {migration_path.name}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


def test_bill_number_generation():
    """Test the bill number generation after migration"""
    print("\nTesting bill number generation...")
    print("-" * 60)

    db = SessionLocal()
    try:
        # Test function 5 times
        numbers = []
        for i in range(5):
            num = db.execute(text("SELECT get_next_bill_number()::text")).scalar()
            numbers.append(num)
            print(f"  Call {i+1}: {num}")

        # Rollback sequence to undo test calls
        db.execute(text(f"SELECT setval('purchase_bill_number_seq', {numbers[0]} - 1, false)"))
        db.commit()

        # Verify uniqueness
        if len(numbers) == len(set(numbers)):
            print("\nResult: All numbers unique - Race condition FIXED!")
            return True
        else:
            print("\nResult: Duplicate numbers detected - Issue persists")
            return False

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Main migration runner"""
    print("=" * 60)
    print("DATABASE MIGRATION RUNNER")
    print("=" * 60)

    # Get migration file path
    if len(sys.argv) > 1:
        migration_file = sys.argv[1]
    else:
        # Default: fix bill number sequence
        migration_file = os.path.join(
            os.path.dirname(__file__),
            'migrations',
            'fix_bill_number_sequence.sql'
        )

    # Run migration
    success = run_migration(migration_file)

    if success:
        # Test if it worked
        test_bill_number_generation()
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("MIGRATION FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
