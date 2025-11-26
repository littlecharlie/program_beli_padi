#!/usr/bin/env python3
"""
Quick installation test for PDF Export Service
Run this to verify the PDF export service is properly installed
"""

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        from services.pdf_export_service import (
            PdfExportService,
            PdfExportError,
            PurchaseBillNotFoundError,
            DeliveryInvoiceNotFoundError,
            InvalidDateRangeError
        )
        print("✓ PDF Export Service imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_reportlab():
    """Test ReportLab installation"""
    print("\nTesting ReportLab...")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate
        from reportlab.lib import colors
        print("✓ ReportLab installed and working")
        return True
    except ImportError as e:
        print(f"✗ ReportLab not installed: {e}")
        print("  Run: pip install reportlab==4.0.7")
        return False


def test_models():
    """Test model imports"""
    print("\nTesting models...")

    try:
        from models.purchase_bill import PurchaseBill
        from models.delivery_invoice import DeliveryInvoice
        from models.farmer import Farmer
        from models.rice_mill import RiceMill
        from models.truck import Truck
        from models.harvest_area import HarvestArea
        print("✓ All models imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Model import failed: {e}")
        return False


def test_formatting():
    """Test formatting functions"""
    print("\nTesting formatting functions...")

    try:
        from services.pdf_export_service import PdfExportService

        # Test currency formatting
        currency = PdfExportService._format_currency(1234.56)
        assert currency == "RM 1,234.56", f"Currency format failed: {currency}"

        # Test weight formatting
        weight = PdfExportService._format_weight(10000.00)
        assert weight == "10,000.00 kg", f"Weight format failed: {weight}"

        # Test date formatting
        from datetime import date
        test_date = date(2025, 11, 26)
        date_str = PdfExportService._format_date(test_date)
        assert date_str == "26/11/2025", f"Date format failed: {date_str}"

        print("✓ All formatting functions working correctly")
        return True
    except Exception as e:
        print(f"✗ Formatting test failed: {e}")
        return False


def test_export_directory():
    """Test export directory creation"""
    print("\nTesting export directory creation...")

    try:
        import os
        from pathlib import Path
        from services.pdf_export_service import PdfExportService

        # Set temp directory for test
        os.environ['PDF_EXPORT_DIR'] = './test_exports_temp'

        export_dir = PdfExportService._get_export_directory()

        assert export_dir.exists(), "Export directory was not created"
        assert export_dir.is_dir(), "Export path is not a directory"

        # Cleanup
        export_dir.rmdir()

        print("✓ Export directory creation working")
        return True
    except Exception as e:
        print(f"✗ Export directory test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")

    try:
        import os
        from dotenv import load_dotenv

        load_dotenv()

        # Check required env vars
        required_vars = [
            'DB_HOST', 'DB_NAME', 'DB_USER',
            'COMPANY_NAME', 'COMPANY_PHONE'
        ]

        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            print(f"⚠ Missing environment variables: {', '.join(missing)}")
            print("  Check your .env file")
        else:
            print("✓ All required configuration present")

        return len(missing) == 0
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("PDF Export Service - Installation Test")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("ReportLab", test_reportlab()))
    results.append(("Models", test_models()))
    results.append(("Formatting", test_formatting()))
    results.append(("Export Directory", test_export_directory()))
    results.append(("Configuration", test_configuration()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed! PDF Export Service is ready to use.")
        print("\nNext steps:")
        print("1. Review PDF_EXPORT_QUICK_START.md for usage examples")
        print("2. Run: pytest tests/test_pdf_export.py -v")
        print("3. Try exporting a purchase bill or delivery invoice")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install ReportLab: pip install reportlab==4.0.7")
        print("- Check .env file has all required variables")
        print("- Ensure all model files are present")

    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
