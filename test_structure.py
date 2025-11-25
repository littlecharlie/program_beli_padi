#!/usr/bin/env python3
"""
Rice Billing System - Structure Verification Test
Tests code structure without requiring PyQt6 or database
"""
import sys
import os

def test_imports():
    """Test that all modules can be imported (syntax check)"""
    print("=" * 60)
    print("TESTING MODULE IMPORTS")
    print("=" * 60)

    modules_to_test = [
        "config.settings",
        "utils.validators",
        "services.calculation_service",
    ]

    success = 0
    failed = 0

    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
            success += 1
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {module}: {type(e).__name__}: {e}")
            failed += 1

    print(f"\nResult: {success} passed, {failed} failed")
    return failed == 0


def test_file_structure():
    """Test that all required files exist"""
    print("\n" + "=" * 60)
    print("TESTING FILE STRUCTURE")
    print("=" * 60)

    required_files = [
        "main.py",
        "requirements.txt",
        ".env",
        "CLAUDE.md",
        "RUN_INSTRUCTIONS.md",
        "config/settings.py",
        "config/database.py",
        "database/connection.py",
        "database/init_schema.sql",
        "models/__init__.py",
        "models/base.py",
        "models/config.py",
        "models/farmer.py",
        "models/purchase_bill.py",
        "models/delivery_invoice.py",
        "services/calculation_service.py",
        "services/purchase_service.py",
        "services/delivery_service.py",
        "ui/main_window.py",
        "ui/styles.py",
        "ui/screens/dashboard.py",
        "ui/screens/purchase_entry.py",
        "ui/screens/purchase_list.py",
        "ui/screens/delivery_entry.py",
        "ui/screens/delivery_list.py",
        "ui/screens/master_data.py",
        "ui/screens/reports.py",
        "ui/screens/settings.py",
        "printing/templates/purchase_template.txt",
        "printing/templates/delivery_template.txt",
    ]

    missing = []
    present = []

    for filepath in required_files:
        full_path = os.path.join(os.getcwd(), filepath)
        if os.path.exists(full_path):
            present.append(filepath)
            print(f"✅ {filepath}")
        else:
            missing.append(filepath)
            print(f"❌ {filepath}")

    print(f"\nResult: {len(present)} files present, {len(missing)} missing")
    return len(missing) == 0


def test_python_syntax():
    """Test Python syntax by compiling key files"""
    print("\n" + "=" * 60)
    print("TESTING PYTHON SYNTAX")
    print("=" * 60)

    import py_compile

    files_to_check = [
        "main.py",
        "config/settings.py",
        "config/database.py",
        "utils/validators.py",
        "services/calculation_service.py",
        "ui/main_window.py",
        "ui/screens/dashboard.py",
        "ui/screens/reports.py",
        "ui/screens/master_data.py",
        "ui/screens/settings.py",
    ]

    success = 0
    failed = 0

    for filepath in files_to_check:
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"✅ {filepath}")
            success += 1
        except py_compile.PyCompileError as e:
            print(f"❌ {filepath}: {e}")
            failed += 1

    print(f"\nResult: {success} files valid, {failed} files with syntax errors")
    return failed == 0


def test_configuration():
    """Test .env configuration"""
    print("\n" + "=" * 60)
    print("TESTING CONFIGURATION")
    print("=" * 60)

    required_keys = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "APP_NAME",
        "DEMO_MODE",
        "DEFAULT_RICE_PRICE",
        "COMPANY_NAME",
    ]

    env_file = ".env"
    config = {}

    if not os.path.exists(env_file):
        print(f"❌ {env_file} not found")
        return False

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()

    success = 0
    missing = []

    for key in required_keys:
        if key in config:
            print(f"✅ {key} = {config[key]}")
            success += 1
        else:
            print(f"❌ {key} missing")
            missing.append(key)

    print(f"\nResult: {success}/{len(required_keys)} keys configured")
    return len(missing) == 0


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "RICE BILLING SYSTEM - STRUCTURE TEST" + " " * 12 + "║")
    print("╚" + "=" * 58 + "╝")

    results = {
        "File Structure": test_file_structure(),
        "Python Syntax": test_python_syntax(),
        "Configuration": test_configuration(),
        "Module Imports": test_imports(),
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nApplication is ready to run!")
        print("\nTo start the application:")
        print("  python main.py")
        print("\nFor detailed setup instructions, see RUN_INSTRUCTIONS.md")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the application.")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
