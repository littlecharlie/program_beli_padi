"""
Build Installer Script for Rice Billing System
Automates the creation of Windows installer using Inno Setup

Prerequisites:
1. Executable already built (run build_executable.py first)
2. Inno Setup 6 installed (https://jrsoftware.org/isinfo.php)

Usage:
    python build_installer.py [--clean]

Output:
    installer_output/RiceBillingSystem_Setup_v1.0.0.exe
"""

import os
import sys
import shutil
import subprocess
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

def find_inno_setup():
    """Find Inno Setup compiler"""
    print_info("Looking for Inno Setup compiler...")

    # Common installation paths
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            print_success(f"Found: {path}")
            return path

    # Try to find in PATH
    try:
        result = subprocess.run(['where', 'ISCC.exe'],
                                capture_output=True,
                                text=True,
                                check=True)
        path = result.stdout.strip().split('\n')[0]
        print_success(f"Found in PATH: {path}")
        return path
    except:
        pass

    return None

def check_prerequisites():
    """Check if all prerequisites are met"""
    print_header("Checking Prerequisites")

    errors = []

    # Check if executable is built
    dist_dir = Path("dist/RiceBillingSystem")
    exe_file = dist_dir / "RiceBillingSystem.exe"

    if not exe_file.exists():
        errors.append("Executable not found. Run 'python build_executable.py' first")
    else:
        exe_size_mb = exe_file.stat().st_size / (1024 * 1024)
        print_success(f"Executable found ({exe_size_mb:.1f} MB)")

    # Check for icon
    icon_file = Path("resources/app_icon.ico")
    if not icon_file.exists():
        errors.append("Icon file not found. Run 'python create_icon.py' first")
    else:
        print_success(f"Icon found")

    # Check for installer script
    iss_file = Path("installer/rice_billing_installer.iss")
    if not iss_file.exists():
        errors.append(f"Installer script not found: {iss_file}")
    else:
        print_success("Installer script found")

    # Check for required installer files
    required_files = [
        "installer/LICENSE.txt",
        "installer/INSTALL_INFO.txt",
        "installer/config_templates/.env.template",
        "installer/scripts/first_run_setup.py",
        "installer/scripts/check_database.py",
        "installer/scripts/cleanup.bat",
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            errors.append(f"Required file missing: {file_path}")
        else:
            print_success(f"Found: {Path(file_path).name}")

    # Check for Inno Setup
    iscc_path = find_inno_setup()
    if not iscc_path:
        errors.append("Inno Setup not found. Install from https://jrsoftware.org/isinfo.php")
    else:
        print_success("Inno Setup compiler ready")

    if errors:
        print()
        print_error("Prerequisites check failed:")
        for error in errors:
            print(f"  - {error}")
        return False, None

    print_success("All prerequisites satisfied")
    return True, iscc_path

def clean_output():
    """Clean installer output directory"""
    print_header("Cleaning Output Directory")

    output_dir = Path("installer_output")
    if output_dir.exists():
        print_info(f"Removing {output_dir}/...")
        shutil.rmtree(output_dir)
        print_success(f"Removed {output_dir}/")
    else:
        print_info(f"{output_dir}/ not found (already clean)")

    print_success("Output directory ready")

def build_installer(iscc_path):
    """Build the installer using Inno Setup"""
    print_header("Building Installer")

    iss_file = Path("installer/rice_billing_installer.iss").absolute()

    print_info(f"Compiling: {iss_file.name}")
    print()

    # Run Inno Setup compiler
    cmd = [iscc_path, str(iss_file)]

    try:
        result = subprocess.run(cmd,
                                capture_output=True,
                                text=True,
                                check=True)

        # Print output
        if result.stdout:
            print(result.stdout)

        print()
        print_success("Installer compiled successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print()
        print_error(f"Compilation failed with error code {e.returncode}")
        if e.stdout:
            print("\nOutput:")
            print(e.stdout)
        if e.stderr:
            print("\nErrors:")
            print(e.stderr)
        return False

def verify_installer():
    """Verify the installer was created"""
    print_header("Verifying Installer")

    output_dir = Path("installer_output")
    if not output_dir.exists():
        print_error("Output directory not found!")
        return False

    # Find installer
    installers = list(output_dir.glob("*.exe"))

    if not installers:
        print_error("No installer found in output directory!")
        return False

    installer = installers[0]
    installer_size_mb = installer.stat().st_size / (1024 * 1024)

    print_success(f"Installer created: {installer.name}")
    print_success(f"Size: {installer_size_mb:.1f} MB")
    print_success(f"Location: {installer.absolute()}")

    print()
    print(f"{Colors.BOLD}Installer is ready for distribution!{Colors.ENDC}")
    print()

    return True

def main():
    """Main build function"""
    import argparse

    parser = argparse.ArgumentParser(description='Build Rice Billing System installer')
    parser.add_argument('--clean', action='store_true',
                        help='Clean output directory before building')
    args = parser.parse_args()

    print_header("Rice Billing System - Installer Builder")
    print_info("Creating professional Windows installer")
    print()

    # Step 1: Check prerequisites
    success, iscc_path = check_prerequisites()
    if not success:
        print_error("Prerequisites check failed. Fix errors above and try again.")
        sys.exit(1)

    # Step 2: Clean output if requested
    if args.clean:
        clean_output()

    # Step 3: Build installer
    if not build_installer(iscc_path):
        print_error("Installer build failed. Check errors above.")
        sys.exit(1)

    # Step 4: Verify installer
    if not verify_installer():
        print_error("Installer verification failed.")
        sys.exit(1)

    # Success!
    print_header("BUILD SUCCESSFUL!")
    print(f"{Colors.OKGREEN}{Colors.BOLD}✓ Installer is ready!{Colors.ENDC}")
    print()
    print(f"{Colors.BOLD}Next steps:{Colors.ENDC}")
    print("  1. Test installer on clean Windows VM")
    print("  2. Try both Database and Demo modes")
    print("  3. Test uninstallation")
    print("  4. Distribute to end users!")
    print()
    print(f"{Colors.BOLD}Installer location:{Colors.ENDC}")

    output_dir = Path("installer_output")
    installers = list(output_dir.glob("*.exe"))
    if installers:
        print(f"  {installers[0].absolute()}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}ERROR: {str(e)}{Colors.ENDC}")
        sys.exit(1)
