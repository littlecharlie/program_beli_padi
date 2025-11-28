# Phase 3: Professional Installer Creation - Complete Guide

**Date:** 2025-11-28
**Branch:** `windows7-compatibility`
**Status:** ✅ READY TO BUILD

---

## Executive Summary

Phase 3 creates a professional Windows installer that provides a complete "double-click to install" experience for end users. The installer includes configuration wizards, database setup, shortcut creation, and proper uninstallation.

### What's Included

✅ Inno Setup installer script (.iss)
✅ Installation wizard with database configuration
✅ License agreement and pre-install information
✅ First-run setup script
✅ Database connection checker
✅ Configuration templates
✅ Automated build script
✅ Uninstaller with cleanup
✅ Complete documentation

---

## Prerequisites

### Required Software

1. **Windows machine** (7, 8, 10, or 11)

2. **Executable already built** (from Phase 2)
   - Must have `dist/RiceBillingSystem/` folder
   - Must contain `RiceBillingSystem.exe`

3. **Inno Setup 6**
   - Download: https://jrsoftware.org/isinfo.php
   - Version: 6.2.0 or later
   - License: Free
   - Size: ~4 MB download

### Installation Folder Structure

```
program_beli_padi/
├── dist/
│   └── RiceBillingSystem/          ← From Phase 2
│       ├── RiceBillingSystem.exe
│       └── ... (all files)
├── resources/
│   └── app_icon.ico                ← From Phase 2
├── installer/                       ← NEW (Phase 3)
│   ├── rice_billing_installer.iss  ← Main installer script
│   ├── LICENSE.txt
│   ├── INSTALL_INFO.txt
│   ├── config_templates/
│   │   ├── .env.template
│   │   └── config.ini.template
│   └── scripts/
│       ├── first_run_setup.py
│       ├── check_database.py
│       └── cleanup.bat
└── build_installer.py               ← Build automation
```

---

## Quick Start - Build Installer

### Step-by-Step Instructions

**1. Ensure executable is built:**
```bash
python build_executable.py --clean
```

**2. Install Inno Setup 6:**
- Download from https://jrsoftware.org/isinfo.php
- Run installer
- Use default settings
- Complete installation

**3. Build the installer:**
```bash
python build_installer.py --clean
```

**4. Find your installer:**
```
installer_output/RiceBillingSystem_Setup_v1.0.0.exe
```

That's it! You now have a professional Windows installer.

---

## Created Files - Detailed Description

### 1. Inno Setup Script

**File:** `installer/rice_billing_installer.iss`

This is the main configuration file for Inno Setup.

**Key Features:**

- **Application Information:**
  - Name: Rice Billing System
  - Version: 1.0.0
  - Publisher: AYOP BIN ARSHAD
  - Windows 7+ compatibility

- **Installation Wizard:**
  - Custom database configuration page
  - Demo mode vs Database mode selection
  - PostgreSQL connection details input
  - Automatic .env file creation

- **Components:**
  - Core application (required)
  - Desktop shortcuts (optional)
  - Start menu shortcuts (optional)
  - Documentation (optional)

- **Registry Integration:**
  - Installation path stored
  - Version information stored
  - Enables future updates

- **Smart Configuration:**
  - Creates .env file automatically
  - Fills in database credentials from wizard
  - Sets demo mode if selected
  - Preserves user settings during upgrades

### 2. License Agreement

**File:** `installer/LICENSE.txt`

Software license agreement shown during installation.

**Content:**
- Grant of license
- Permitted use and restrictions
- Data privacy notice
- No warranty disclaimer
- Limitation of liability
- Third-party component licenses

Users must accept before installation proceeds.

### 3. Installation Information

**File:** `installer/INSTALL_INFO.txt`

Pre-installation information shown to users.

**Contains:**
- System requirements
- Installation modes explained (Database vs Demo)
- PostgreSQL requirements
- Printer requirements
- Installation steps overview
- Post-installation tasks
- Troubleshooting quick tips

### 4. Configuration Templates

**Files:**
- `installer/config_templates/.env.template`
- `installer/config_templates/config.ini.template`

Template configuration files that are copied during installation.

**.env.template:**
- Database connection settings
- Demo mode flag
- Business configuration defaults
- Printer settings
- Logging configuration

**config.ini.template:**
- Application settings
- Window size and position
- Backup configuration
- Export settings
- UI preferences

### 5. First-Run Setup Script

**File:** `installer/scripts/first_run_setup.py`

Optional post-installation script that verifies setup.

**Features:**
- Checks .env file exists and is configured
- Tests database connection (if not demo mode)
- Creates necessary directories (exports, backups, logs)
- Provides clear feedback on configuration status
- Guides user to fix any issues

**Usage:**
- Can be run automatically after installation
- Or manually from Start Menu
- Helps diagnose configuration problems

### 6. Database Connection Checker

**File:** `installer/scripts/check_database.py`

Standalone tool to test database connectivity.

**Features:**
- Reads database config from .env
- Tests PostgreSQL connection
- Shows database version
- Counts tables in database
- Provides troubleshooting guidance
- Can be run anytime from Start Menu

**When to use:**
- After installation to verify database
- When connection problems occur
- Before running the main application
- To diagnose PostgreSQL issues

### 7. Cleanup Script

**File:** `installer/scripts/cleanup.bat`

Runs before uninstallation.

**What it removes:**
- Log files (*.log)
- Python cache (__pycache__)
- Temporary files

**What it preserves:**
- .env file (user configuration)
- exports/ folder (user data)
- backups/ folder (user data)
- Database (stored in PostgreSQL)

Users can manually delete preserved data if desired.

### 8. Build Automation Script

**File:** `build_installer.py`

Automated script to build the installer.

**Features:**
- Checks all prerequisites
- Finds Inno Setup compiler automatically
- Compiles installer script
- Verifies output
- Shows file size and location
- Handles errors gracefully

**Usage:**
```bash
# Basic build
python build_installer.py

# Clean build
python build_installer.py --clean
```

---

## Installation Wizard Flow

### User Experience

**1. Welcome Screen**
- Shows application name and version
- Brief description
- "Next" to continue

**2. License Agreement**
- Shows LICENSE.txt content
- User must accept to proceed
- "I accept" checkbox

**3. Pre-Installation Information**
- Shows INSTALL_INFO.txt
- System requirements
- Important notices
- Preparation steps

**4. Installation Folder**
- Default: C:\Program Files\Rice Billing System
- User can change if desired
- Checks for admin rights

**5. Component Selection**
- Core Application (fixed, required)
- Desktop Shortcut (optional, checked)
- Start Menu Shortcuts (optional, checked)
- Documentation (optional, checked)

**6. Database Configuration** ⭐ CUSTOM PAGE
- **Choice 1:** Use PostgreSQL Database
  - For production use
  - Requires PostgreSQL installed
  - Shows database configuration inputs:
    - Host (default: localhost)
    - Port (default: 5432)
    - Database Name (default: rice_billing_db)
    - Username (default: postgres)
    - Password (user must enter)

- **Choice 2:** Demo Mode
  - For testing/evaluation
  - No database needed
  - Limited functionality
  - Data not saved

**7. Ready to Install**
- Summary of selections
- Install location
- Space required
- "Install" button

**8. Installing**
- Progress bar
- Shows files being copied
- Configures .env file
- Sets up shortcuts

**9. Completing Installation**
- Installation successful message
- Options:
  - ✓ Launch Rice Billing System
  - ○ Run first-time configuration
  - ○ View README file
- "Finish" button

---

## Post-Installation Structure

After installation, the user has:

```
C:\Program Files\Rice Billing System\
├── RiceBillingSystem.exe           # Main application
├── _internal/                       # Dependencies
├── printing/
│   └── templates/
├── resources/
│   ├── app_icon.ico
│   └── app_icon.png
├── scripts/
│   ├── first_run_setup.py
│   ├── check_database.py
│   └── cleanup.bat
├── .env                             # Created by installer!
├── .env.example
├── config.ini
├── LICENSE.txt
├── INSTALL_INFO.txt
└── README.txt

Desktop\
└── Rice Billing System.lnk         # Desktop shortcut

Start Menu\Programs\Rice Billing System\
├── Rice Billing System.lnk
├── Configure Database.lnk
├── User Guide.lnk
└── Uninstall.lnk
```

---

## Building the Installer

### Method 1: Automated (Recommended)

```bash
python build_installer.py --clean
```

This script:
1. Checks prerequisites
2. Finds Inno Setup compiler
3. Compiles installer
4. Verifies output
5. Shows result

### Method 2: Manual with Inno Setup IDE

1. Open Inno Setup
2. File → Open → `installer/rice_billing_installer.iss`
3. Build → Compile
4. Wait for compilation
5. Output in `installer_output/`

### Method 3: Command Line

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\rice_billing_installer.iss
```

---

## Installer Output

**File:** `installer_output/RiceBillingSystem_Setup_v1.0.0.exe`

**Size:** Approximately 150-200 MB
- Includes all application files
- Includes dependencies
- Compressed with LZMA2

**Compression:** LZMA2/maximum
- Best compression available in Inno Setup
- Reduces installer size by ~40%
- Slightly slower installation (acceptable)

---

## Testing the Installer

### Test 1: Clean Windows 7 VM

**Setup:**
1. Create Windows 7 SP1 virtual machine
2. No development tools installed
3. No Python installed
4. Fresh, clean system

**Test Demo Mode:**
1. Run installer
2. Choose Demo Mode
3. Complete installation
4. Launch application
5. Verify it runs without database
6. Test all screens accessible
7. Uninstall
8. Verify clean removal

**Test Database Mode:**
1. Install PostgreSQL 13
2. Create database `rice_billing_db`
3. Run installer
4. Choose Database Mode
5. Enter database credentials
6. Complete installation
7. Launch application
8. Verify database connection
9. Create a purchase bill
10. Verify data saved to database
11. Restart application
12. Verify data persists

### Test 2: Upgrade Installation

**Test upgrade process:**
1. Install version 1.0.0
2. Create some test data
3. Build version 1.0.1 (change version in .iss)
4. Install version 1.0.1 over 1.0.0
5. Verify .env file preserved
6. Verify data preserved
7. Verify upgrade successful

### Test 3: Different Component Combinations

Test various installation options:
- With/without desktop shortcut
- With/without documentation
- Different installation folders
- Custom vs Full installation

### Test 4: Uninstallation

**Verify clean uninstall:**
1. Install application
2. Create some test files
3. Run uninstaller
4. Check Program Files → folder deleted
5. Check Start Menu → shortcuts removed
6. Check Desktop → shortcut removed
7. Check Registry → entries removed
8. Verify exports/ and backups/ preserved (if created)

---

## Troubleshooting

### Inno Setup Not Found

**Error:** `ISCC.exe not found`

**Solutions:**
1. Install Inno Setup 6 from https://jrsoftware.org/isinfo.php
2. Use default installation path
3. Or manually specify path in build_installer.py

### Executable Not Found

**Error:** `Executable not found`

**Solution:**
```bash
python build_executable.py --clean
```

### Missing Files Error

**Error:** `Required file missing: installer/LICENSE.txt`

**Solution:**
All installer files must be present:
- installer/LICENSE.txt
- installer/INSTALL_INFO.txt
- installer/config_templates/.env.template
- installer/scripts/*.py

Ensure you have all Phase 3 files.

### Compilation Errors

**Error:** Parse error in .iss file

**Solution:**
- Check .iss file syntax
- Ensure all paths exist
- Verify file references are correct
- Check for missing semicolons

### Installer Too Large

**Current size:** ~150-200 MB (normal for PyQt5 app)

**To reduce:**
- Already using maximum LZMA2 compression
- Size is determined by executable size
- Cannot reduce significantly without removing features

### Installation Fails on Windows 7

**Error:** `This app can't run on your PC`

**Causes:**
- Windows 7 SP1 required (not RTM)
- .NET Framework 4.5+ required

**Solutions:**
- Install Windows 7 Service Pack 1
- Install .NET Framework 4.5 or later
- Run Windows Update

---

## Customization Options

### Change Application Name

Edit `installer/rice_billing_installer.iss`:
```pascal
#define MyAppName "Your App Name"
```

### Change Version Number

```pascal
#define MyAppVersion "1.0.1"
```

### Change Publisher

```pascal
#define MyAppPublisher "Your Company Name"
```

### Change Default Installation Folder

```pascal
DefaultDirName={autopf}\YourAppFolder
```

### Add Custom Wizard Pages

You can add more custom pages by modifying the `[Code]` section.

### Modify License or Info Files

Simply edit:
- `installer/LICENSE.txt`
- `installer/INSTALL_INFO.txt`

### Change Icon

Replace `resources/app_icon.ico` with your custom icon.

---

## Advanced Features

### Silent Installation

Users can install silently (no UI):
```bash
RiceBillingSystem_Setup_v1.0.0.exe /SILENT
```

Or very silent (no UI, no progress):
```bash
RiceBillingSystem_Setup_v1.0.0.exe /VERYSILENT
```

### Custom Installation Parameters

```bash
# Install to specific directory
Setup.exe /DIR="C:\MyFolder"

# Skip specific tasks
Setup.exe /TASKS="!desktopicon"

# Install specific components
Setup.exe /COMPONENTS="core,shortcuts"
```

### Logging

Enable installation log:
```bash
Setup.exe /LOG="C:\install.log"
```

### Digital Signing

For production, sign the installer:
1. Obtain code signing certificate
2. Sign with SignTool:
```bash
signtool sign /f certificate.pfx /p password Setup.exe
```

---

## Distribution

### Upload to Website

**Best for:** Public distribution

```
1. Upload RiceBillingSystem_Setup_v1.0.0.exe
2. Provide download link
3. Include SHA256 checksum
4. Provide installation instructions
```

### USB/Physical Media

**Best for:** Offline distribution

```
1. Copy installer to USB drive
2. Include README.txt with instructions
3. Include printer driver installer
4. Include PostgreSQL installer (optional)
```

### Network Share

**Best for:** Company network

```
1. Place on network share
2. Users run from \\server\share\Setup.exe
3. Can enable silent installation
4. Can automate with Group Policy
```

---

## File Checklist

Make sure these files exist after Phase 3:

- [ ] `installer/rice_billing_installer.iss` - Main installer script
- [ ] `installer/LICENSE.txt` - License agreement
- [ ] `installer/INSTALL_INFO.txt` - Pre-installation info
- [ ] `installer/config_templates/.env.template` - Environment template
- [ ] `installer/config_templates/config.ini.template` - Config template
- [ ] `installer/scripts/first_run_setup.py` - Setup verification
- [ ] `installer/scripts/check_database.py` - Database checker
- [ ] `installer/scripts/cleanup.bat` - Uninstall cleanup
- [ ] `build_installer.py` - Build automation
- [ ] `PHASE3_INSTALLER_CREATION.md` - This documentation

---

## Summary

✅ **Phase 3 Complete - Professional Installer Ready**

**What you have:**
- Professional installation wizard
- Database configuration wizard
- Automatic .env creation
- First-run setup verification
- Desktop and Start Menu shortcuts
- Clean uninstallation
- Complete documentation

**What you can do:**
- Build installer with one command
- Distribute to end users
- Support both demo and database modes
- Professional deployment experience

**What's next:**
- Test on Windows 7 VM
- Distribute to users
- Proceed to Phase 4 (documentation) if needed

---

**Created by:** Claude Code
**Date:** 2025-11-28
**Branch:** windows7-compatibility
**Status:** Ready to build installer
