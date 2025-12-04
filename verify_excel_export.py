#!/usr/bin/env python3
"""
Verification script for Excel export implementation
Checks that all components are properly installed and configured
"""
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^70}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

def print_check(name, passed, details=""):
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{name:.<50} {status}")
    if details and not passed:
        print(f"  {Colors.YELLOW}→ {details}{Colors.RESET}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    required = (3, 8)
    passed = version >= required
    details = f"Found {version.major}.{version.minor}.{version.micro}, requires >= {required[0]}.{required[1]}"
    if not passed:
        details = f"{details} - UPGRADE REQUIRED"
    return passed, details

def check_openpyxl():
    """Check if openpyxl is installed"""
    try:
        import openpyxl
        version = openpyxl.__version__
        passed = True
        details = f"Version {version} installed"
    except ImportError:
        passed = False
        details = "Not installed - run: pip install openpyxl==3.1.2"
    return passed, details

def check_service_file():
    """Check if excel_export_service.py exists"""
    file_path = Path(__file__).parent / "services" / "excel_export_service.py"
    passed = file_path.exists()
    details = str(file_path) if passed else "File not found"
    return passed, details

def check_service_class():
    """Check if ExcelExportService class is importable"""
    try:
        from services.excel_export_service import ExcelExportService
        passed = True

        # Check methods exist
        required_methods = [
            'export_purchase_bills',
            'export_delivery_invoices',
            'export_farmer_summary',
            'export_mill_summary'
        ]

        for method in required_methods:
            if not hasattr(ExcelExportService, method):
                passed = False
                details = f"Missing method: {method}"
                return passed, details

        details = "All 4 export methods present"
    except ImportError as e:
        passed = False
        details = f"Import error: {str(e)}"
    except Exception as e:
        passed = False
        details = f"Error: {str(e)}"

    return passed, details

def check_reports_ui():
    """Check if reports.py has been updated"""
    file_path = Path(__file__).parent / "ui" / "screens" / "reports.py"

    if not file_path.exists():
        return False, "File not found"

    try:
        content = file_path.read_text()

        # Check for key imports
        has_excel_import = "excel_export_service" in content
        has_excel_error = "ExcelExportError" in content

        # Check for export_excel method implementation
        has_export_method = "def export_excel(self):" in content
        has_excel_service_call = "ExcelExportService.export_" in content

        passed = all([has_excel_import, has_excel_error, has_export_method, has_excel_service_call])

        if passed:
            details = "UI properly integrated"
        else:
            missing = []
            if not has_excel_import: missing.append("import")
            if not has_excel_error: missing.append("error handling")
            if not has_export_method: missing.append("export method")
            if not has_excel_service_call: missing.append("service calls")
            details = f"Missing: {', '.join(missing)}"

    except Exception as e:
        passed = False
        details = f"Error reading file: {str(e)}"

    return passed, details

def check_requirements():
    """Check if requirements.txt has openpyxl"""
    file_path = Path(__file__).parent / "requirements.txt"

    if not file_path.exists():
        return False, "requirements.txt not found"

    try:
        content = file_path.read_text()
        passed = "openpyxl" in content
        details = "openpyxl listed in requirements.txt" if passed else "openpyxl not in requirements.txt"
    except Exception as e:
        passed = False
        details = f"Error: {str(e)}"

    return passed, details

def check_documentation():
    """Check if documentation files exist"""
    base_path = Path(__file__).parent
    docs = [
        "EXCEL_EXPORT_IMPLEMENTATION.md",
        "EXCEL_EXPORT_QUICK_START.md",
        "EXCEL_EXPORT_SUMMARY.md"
    ]

    missing = []
    for doc in docs:
        if not (base_path / doc).exists():
            missing.append(doc)

    passed = len(missing) == 0
    if passed:
        details = "All 3 documentation files present"
    else:
        details = f"Missing: {', '.join(missing)}"

    return passed, details

def check_test_file():
    """Check if test file exists"""
    file_path = Path(__file__).parent / "test_excel_export.py"
    passed = file_path.exists()
    details = "Test suite present" if passed else "test_excel_export.py not found"
    return passed, details

def check_database_models():
    """Check if required models are importable"""
    try:
        from models.purchase_bill import PurchaseBill
        from models.delivery_invoice import DeliveryInvoice
        from models.farmer import Farmer
        from models.rice_mill import RiceMill
        passed = True
        details = "All required models importable"
    except ImportError as e:
        passed = False
        details = f"Model import error: {str(e)}"
    except Exception as e:
        passed = False
        details = f"Error: {str(e)}"

    return passed, details

def check_database_connection():
    """Check if database connection works"""
    try:
        from config.database import get_db
        db = get_db()
        passed = db is not None
        details = "Database connection successful"
    except Exception as e:
        passed = False
        details = f"Connection error: {str(e)}"

    return passed, details

def main():
    """Run all verification checks"""
    print_header("EXCEL EXPORT VERIFICATION")

    print(f"{Colors.BOLD}Checking Python Environment...{Colors.RESET}\n")

    checks = [
        ("Python Version", check_python_version),
        ("openpyxl Library", check_openpyxl),
    ]

    for name, check_func in checks:
        passed, details = check_func()
        print_check(name, passed, details)

    print(f"\n{Colors.BOLD}Checking Implementation Files...{Colors.RESET}\n")

    checks = [
        ("Excel Export Service File", check_service_file),
        ("ExcelExportService Class", check_service_class),
        ("Reports UI Integration", check_reports_ui),
        ("Requirements.txt Updated", check_requirements),
        ("Test Suite", check_test_file),
        ("Documentation Files", check_documentation),
    ]

    for name, check_func in checks:
        passed, details = check_func()
        print_check(name, passed, details)

    print(f"\n{Colors.BOLD}Checking Dependencies...{Colors.RESET}\n")

    checks = [
        ("Database Models", check_database_models),
        ("Database Connection", check_database_connection),
    ]

    for name, check_func in checks:
        passed, details = check_func()
        print_check(name, passed, details)

    print_header("VERIFICATION COMPLETE")

    # Summary
    all_checks = [
        check_python_version,
        check_openpyxl,
        check_service_file,
        check_service_class,
        check_reports_ui,
        check_requirements,
        check_test_file,
        check_documentation,
        check_database_models,
        check_database_connection,
    ]

    results = [check_func()[0] for check_func in all_checks]
    passed = sum(results)
    total = len(results)

    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  Total Checks: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {total - passed}{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED{Colors.RESET}")
        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print("  1. Run test suite: python test_excel_export.py")
        print("  2. Launch application and test UI")
        print("  3. Review documentation: EXCEL_EXPORT_QUICK_START.md")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED{Colors.RESET}")
        print(f"\n{Colors.BOLD}Actions Required:{Colors.RESET}")
        print("  1. Review failed checks above")
        print("  2. Install missing dependencies: pip install -r requirements.txt")
        print("  3. Re-run this verification: python verify_excel_export.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
