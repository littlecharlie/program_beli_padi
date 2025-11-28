# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Rice Billing System
Windows 7 compatible executable

Build command:
    pyinstaller rice_billing.spec

Or use the build script:
    python build_executable.py
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Application metadata
APP_NAME = 'RiceBillingSystem'
VERSION = '1.0.0'
COMPANY_NAME = 'AYOP BIN ARSHAD'
COPYRIGHT = '© 2024 AYOP BIN ARSHAD'

# Paths
spec_root = os.path.abspath(SPECPATH)
icon_path = os.path.join(spec_root, 'resources', 'app_icon.ico')

# Data files to include
datas = [
    # Receipt templates
    ('printing/templates/*.txt', 'printing/templates'),

    # Application icon (for runtime use if needed)
    ('resources/app_icon.ico', 'resources'),
    ('resources/app_icon.png', 'resources'),
]

# Hidden imports - packages not automatically detected
hiddenimports = [
    # PyQt5 modules
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtPrintSupport',

    # Database
    'psycopg2',
    'psycopg2.extensions',
    'sqlalchemy',
    'sqlalchemy.dialects.postgresql',
    'sqlalchemy.engine',
    'sqlalchemy.orm',
    'sqlalchemy.pool',
    'alembic',

    # Printing
    'escpos',
    'escpos.printer',
    'escpos.constants',
    'win32print',  # Windows printer support
    'win32ui',
    'pywintypes',

    # PDF
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'reportlab.platypus',

    # Utilities
    'dotenv',
    'dateutil',
    'loguru',

    # API (optional, for future use)
    'fastapi',
    'uvicorn',
    'pydantic',
]

# Collect all submodules for critical packages
hiddenimports += collect_submodules('sqlalchemy')
hiddenimports += collect_submodules('alembic')
hiddenimports += collect_submodules('reportlab')

# Binaries to exclude (reduce size)
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'jupyter',
    'IPython',
    'notebook',
]

a = Analysis(
    ['main.py'],
    pathex=[spec_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# Option 1: ONE-FOLDER distribution (recommended for first testing)
# Pros: Faster to build, easier to debug
# Cons: Multiple files in folder

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging to see console output
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    version_file=None,  # Can add version info file later
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# Option 2: ONE-FILE distribution (uncomment to use)
# Pros: Single .exe file
# Cons: Slower startup (extracts to temp), larger file size
# To use: Comment out Option 1 above and uncomment below

"""
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
"""

# Build info
print("=" * 60)
print(f"Building: {APP_NAME} v{VERSION}")
print(f"Company: {COMPANY_NAME}")
print(f"Icon: {icon_path}")
print(f"Mode: ONE-FOLDER")  # Change if using ONE-FILE
print(f"Console: {'Enabled' if exe.console else 'Disabled'}")
print("=" * 60)
