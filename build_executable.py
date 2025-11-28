"""
Automated build script for Rice Billing System executable
Builds Windows executable compatible with Windows 7

Usage:
    python build_executable.py [--clean] [--onefile]

Options:
    --clean     Clean build directories before building
    --onefile   Build as single executable file (default: folder)
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{msg}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")

def check_requirements():
    """Check if all required tools and files are present"""
    print_header("Checking Requirements")

    errors = []

    # Check Python version
    print_info(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        errors.append("Python 3.8 or higher is required")
    else:
        print_success("Python version OK")

    # Check PyInstaller
    try:
        import PyInstaller
        print_success(f"PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        errors.append("PyInstaller not installed. Run: pip install pyinstaller")

    # Check for icon
    icon_path = Path("resources/app_icon.ico")
    if not icon_path.exists():
        errors.append(f"Icon file not found: {icon_path}")
        print_warning(f"Icon missing. Run: python create_icon.py")
    else:
        print_success(f"Icon found: {icon_path}")

    # Check for spec file
    spec_path = Path("rice_billing.spec")
    if not spec_path.exists():
        errors.append(f"Spec file not found: {spec_path}")
    else:
        print_success(f"Spec file found: {spec_path}")

    # Check for main.py
    main_path = Path("main.py")
    if not main_path.exists():
        errors.append("main.py not found")
    else:
        print_success("main.py found")

    # Check for templates
    template_dir = Path("printing/templates")
    if not template_dir.exists():
        errors.append(f"Template directory not found: {template_dir}")
    else:
        templates = list(template_dir.glob("*.txt"))
        print_success(f"Found {len(templates)} template files")

    if errors:
        print_error("Requirements check failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    print_success("All requirements satisfied")
    return True

def clean_build_dirs():
    """Clean build and dist directories"""
    print_header("Cleaning Build Directories")

    dirs_to_clean = ['build', 'dist', '__pycache__']

    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_info(f"Removing {dir_name}/...")
            shutil.rmtree(dir_path)
            print_success(f"Removed {dir_name}/")
        else:
            print_info(f"{dir_name}/ not found (already clean)")

    # Clean .spec cache files
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()

    print_success("Build directories cleaned")

def build_executable(onefile=False):
    """Build the executable using PyInstaller"""
    print_header("Building Executable")

    # Update spec file if onefile is requested
    spec_file = "rice_billing.spec"

    if onefile:
        print_info("Building as SINGLE FILE executable")
        print_warning("Note: Single file may be slower to start")
    else:
        print_info("Building as FOLDER executable")

    # Run PyInstaller
    cmd = ['pyinstaller', '--clean', spec_file]

    print_info(f"Running: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True)
        print()
        print_success("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print_error(f"Build failed with error code {e.returncode}")
        return False

def verify_build():
    """Verify the build output"""
    print_header("Verifying Build")

    dist_dir = Path("dist/RiceBillingSystem")

    if not dist_dir.exists():
        print_error(f"Build directory not found: {dist_dir}")
        return False

    # Check for executable
    exe_file = dist_dir / "RiceBillingSystem.exe"
    if not exe_file.exists():
        print_error(f"Executable not found: {exe_file}")
        return False

    exe_size_mb = exe_file.stat().st_size / (1024 * 1024)
    print_success(f"Executable found: {exe_file.name} ({exe_size_mb:.1f} MB)")

    # Check for templates
    templates_dir = dist_dir / "printing" / "templates"
    if templates_dir.exists():
        template_count = len(list(templates_dir.glob("*.txt")))
        print_success(f"Templates included: {template_count} files")
    else:
        print_warning("Templates directory not found in build")

    # List all files in dist
    all_files = list(dist_dir.rglob("*"))
    file_count = len([f for f in all_files if f.is_file()])
    total_size_mb = sum(f.stat().st_size for f in all_files if f.is_file()) / (1024 * 1024)

    print_success(f"Total files: {file_count}")
    print_success(f"Total size: {total_size_mb:.1f} MB")

    print()
    print_success("Build verification passed!")
    print()
    print(f"{Colors.BOLD}Executable location:{Colors.ENDC}")
    print(f"  {exe_file.absolute()}")
    print()

    return True

def create_deployment_package():
    """Create deployment package with necessary files"""
    print_header("Creating Deployment Package")

    dist_dir = Path("dist/RiceBillingSystem")
    if not dist_dir.exists():
        print_error("Build directory not found. Build executable first.")
        return False

    # Create .env.example in dist directory
    env_example_path = dist_dir / ".env.example"
    env_example_content = """# Rice Billing System Configuration
# Copy this file to .env and configure for your environment

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rice_billing_db
DB_USER=postgres
DB_PASSWORD=your_password_here

# Demo Mode (set to true to run without database)
DEMO_MODE=false

# Business Configuration (loaded from database, these are fallbacks)
DEFAULT_RICE_PRICE=1500.00
DEFAULT_SUBSIDY_RATE=0.50
DEFAULT_DISCOUNT_WAP_BASAH=7.00
DEFAULT_DISCOUNT_HAMPA_PADI=7.00
DEFAULT_DISCOUNT_PADI_MUDA=6.00

# Printer Configuration
PRINTER_NAME=EPSON LQ-310
PRINTER_INTERFACE=usb

# Logging
LOG_LEVEL=INFO
"""
    env_example_path.write_text(env_example_content)
    print_success("Created .env.example")

    # Create README.txt
    readme_path = dist_dir / "README.txt"
    readme_content = """RICE BILLING SYSTEM - QUICK START
===================================

REQUIREMENTS:
- Windows 7 or later
- PostgreSQL 13+ installed and running
- Epson LQ-310 printer driver installed

INSTALLATION:
1. Copy this entire folder to C:\\Program Files\\RiceBillingSystem\\
2. Copy .env.example to .env
3. Edit .env file with your database credentials
4. Double-click RiceBillingSystem.exe to run

DEMO MODE (No Database):
1. Copy .env.example to .env
2. Set DEMO_MODE=true in .env file
3. Run RiceBillingSystem.exe

FIRST-TIME SETUP:
- The application will create database tables automatically on first run
- Configure company details in Settings screen
- Add farmers, mills, trucks, and harvest areas in Master Data screen

PRINTER SETUP:
- Install Epson LQ-310 driver from Epson website
- Connect printer via USB
- Configure printer name in .env file

TROUBLESHOOTING:
- Check that PostgreSQL service is running
- Verify database credentials in .env file
- For demo mode testing, set DEMO_MODE=true
- Check logs in the application folder

SUPPORT:
For issues, contact: support@example.com

Version: 1.0.0
Compatible with: Windows 7, 8, 10, 11
"""
    readme_path.write_text(readme_content)
    print_success("Created README.txt")

    print_success("Deployment package ready!")
    print()
    print(f"{Colors.BOLD}Package location:{Colors.ENDC}")
    print(f"  {dist_dir.absolute()}")
    print()
    print(f"{Colors.BOLD}Next steps:{Colors.ENDC}")
    print("  1. Test the executable on this machine")
    print("  2. Test on a clean Windows 7 virtual machine")
    print("  3. Create installer with Inno Setup (Phase 3)")
    print()

    return True

def main():
    parser = argparse.ArgumentParser(description='Build Rice Billing System executable')
    parser.add_argument('--clean', action='store_true', help='Clean build directories first')
    parser.add_argument('--onefile', action='store_true', help='Build as single file (not recommended)')
    args = parser.parse_args()

    print_header("Rice Billing System - Executable Builder")
    print_info("Target: Windows 7+ Compatible Executable")
    print_info("Python: 3.8+ Required")
    print()

    # Step 1: Check requirements
    if not check_requirements():
        print_error("Requirements check failed. Please fix errors above.")
        sys.exit(1)

    # Step 2: Clean if requested
    if args.clean:
        clean_build_dirs()

    # Step 3: Build executable
    if not build_executable(onefile=args.onefile):
        print_error("Build failed. Check errors above.")
        sys.exit(1)

    # Step 4: Verify build
    if not verify_build():
        print_error("Build verification failed.")
        sys.exit(1)

    # Step 5: Create deployment package
    if not create_deployment_package():
        print_error("Failed to create deployment package.")
        sys.exit(1)

    # Final success message
    print_header("BUILD SUCCESSFUL!")
    print(f"{Colors.OKGREEN}{Colors.BOLD}✓ Rice Billing System executable is ready!{Colors.ENDC}")
    print()
    print(f"{Colors.BOLD}What to do next:{Colors.ENDC}")
    print("  1. Test: Run dist/RiceBillingSystem/RiceBillingSystem.exe")
    print("  2. Package: Create installer with Inno Setup (see Phase 3 docs)")
    print("  3. Deploy: Distribute to Windows 7 machines")
    print()

if __name__ == "__main__":
    main()
