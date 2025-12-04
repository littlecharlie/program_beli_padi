"""
Test script for Excel export functionality
Run this to verify the Excel export service works correctly
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config.database import get_db
from services.excel_export_service import ExcelExportService, ExcelExportError


def test_export_purchase_bills():
    """Test purchase bills export"""
    print("Testing Purchase Bills Export...")

    db = get_db()

    # Set date range for last 30 days
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)

    # Create output directory
    output_dir = Path.home() / "Documents" / "test_exports"
    output_dir.mkdir(exist_ok=True, parents=True)

    file_path = str(output_dir / f"test_purchase_bills_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

    try:
        result = ExcelExportService.export_purchase_bills(
            db=db,
            file_path=file_path,
            from_date=from_date,
            to_date=to_date,
            filter_id=None
        )
        print(f"SUCCESS: Purchase bills exported to {result}")
        return True
    except ExcelExportError as e:
        print(f"ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False


def test_export_delivery_invoices():
    """Test delivery invoices export"""
    print("\nTesting Delivery Invoices Export...")

    db = get_db()

    # Set date range for last 30 days
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)

    # Create output directory
    output_dir = Path.home() / "Documents" / "test_exports"
    output_dir.mkdir(exist_ok=True, parents=True)

    file_path = str(output_dir / f"test_delivery_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

    try:
        result = ExcelExportService.export_delivery_invoices(
            db=db,
            file_path=file_path,
            from_date=from_date,
            to_date=to_date,
            filter_id=None
        )
        print(f"SUCCESS: Delivery invoices exported to {result}")
        return True
    except ExcelExportError as e:
        print(f"ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False


def test_export_farmer_summary():
    """Test farmer summary export"""
    print("\nTesting Farmer Summary Export...")

    db = get_db()

    # Set date range for last 30 days
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)

    # Create output directory
    output_dir = Path.home() / "Documents" / "test_exports"
    output_dir.mkdir(exist_ok=True, parents=True)

    file_path = str(output_dir / f"test_farmer_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

    try:
        result = ExcelExportService.export_farmer_summary(
            db=db,
            file_path=file_path,
            from_date=from_date,
            to_date=to_date,
            filter_id=None
        )
        print(f"SUCCESS: Farmer summary exported to {result}")
        return True
    except ExcelExportError as e:
        print(f"ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False


def test_export_mill_summary():
    """Test mill summary export"""
    print("\nTesting Mill Summary Export...")

    db = get_db()

    # Set date range for last 30 days
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)

    # Create output directory
    output_dir = Path.home() / "Documents" / "test_exports"
    output_dir.mkdir(exist_ok=True, parents=True)

    file_path = str(output_dir / f"test_mill_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

    try:
        result = ExcelExportService.export_mill_summary(
            db=db,
            file_path=file_path,
            from_date=from_date,
            to_date=to_date,
            filter_id=None
        )
        print(f"SUCCESS: Mill summary exported to {result}")
        return True
    except ExcelExportError as e:
        print(f"ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("EXCEL EXPORT SERVICE TEST SUITE")
    print("=" * 70)

    results = []

    # Test each export type
    results.append(("Purchase Bills", test_export_purchase_bills()))
    results.append(("Delivery Invoices", test_export_delivery_invoices()))
    results.append(("Farmer Summary", test_export_farmer_summary()))
    results.append(("Mill Summary", test_export_mill_summary()))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:30s} [{status}]")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {total} | Passed: {passed} | Failed: {total - passed}")

    if passed == total:
        print("\nAll tests passed successfully!")
    else:
        print(f"\n{total - passed} test(s) failed. Please check the errors above.")

    print("\nExported files location: ~/Documents/test_exports/")


if __name__ == "__main__":
    main()
