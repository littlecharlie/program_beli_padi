# Windows 7 Installation Quickstart

## Prerequisites
- Windows 7 (32-bit or 64-bit)
- Python 3.7.6 installed
- pip installed

## Installation Steps

### 1. Install Dependencies
```cmd
pip install -r requirements-python37.txt
```

This will install:
- PyQt5 (desktop UI) **with pre-built wheels - no compiler needed!**
- PostgreSQL database drivers
- Printing support
- PDF generation
- All utilities

**Note:** FastAPI/uvicorn are commented out (not needed for desktop app)

### 2. Configure Environment
Create `.env` file:
```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rice_billing_db
DB_USER=postgres
DB_PASSWORD=your_password

# Demo mode (set to true if no database)
DEMO_MODE=false
```

### 3. Run the Application
```cmd
python main.py
```

## Troubleshooting

### Error: "Could not find uvicorn==0.24.0"
**Fixed!** This error should not occur anymore. The requirements file has been updated.

If you still see this error:
1. Make sure you're using the latest `requirements-python37.txt`
2. FastAPI/uvicorn should be commented out (lines 28-30)

### Error: "Microsoft Visual C++ 14.0 is required" (PyQt5-sip)
**Fixed!** The requirements file now includes PyQt5-sip==12.13.0 with pre-built wheels.

If you still see this error:
1. Clear pip cache: `pip cache purge`
2. Uninstall: `pip uninstall PyQt5 PyQt5-sip -y`
3. Reinstall: `pip install PyQt5-sip==12.13.0 PyQt5==5.15.10`
4. See **[PYQT5_WINDOWS7_INSTALL_GUIDE.md](PYQT5_WINDOWS7_INSTALL_GUIDE.md)** for comprehensive troubleshooting

### Want to Run API Examples?
Only needed for future mobile development.

1. Edit `requirements-python37.txt`
2. Uncomment lines 28-30:
   ```
   fastapi==0.100.1
   uvicorn==0.23.2
   pydantic==1.10.13
   ```
3. Run: `pip install -r requirements-python37.txt`

## What's Installed

### Core Desktop App (Always Installed)
- **PyQt5-sip 12.13.0** - PyQt5 bindings (pre-built wheel)
- **PyQt5 5.15.10** - Desktop UI framework
- **psycopg2-binary 2.9.9** - PostgreSQL database
- **SQLAlchemy 1.4.53** - Database ORM
- **python-escpos 2.2.0** - Epson printer support
- **reportlab 3.6.13** - PDF generation
- **pywin32 306** - Windows integration

### Optional API (Commented Out)
- **fastapi** - Web API framework (not needed for desktop)
- **uvicorn** - ASGI server (not needed for desktop)
- **pydantic** - Data validation (not needed for desktop)

## File Locations

- **Requirements:** `/home/appfelix/claude/program_beli_padi/requirements-python37.txt`
- **Main App:** `/home/appfelix/claude/program_beli_padi/main.py`
- **PyQt5 Fix Guide:** `/home/appfelix/claude/program_beli_padi/PYQT5_WINDOWS7_INSTALL_GUIDE.md`
- **FastAPI Fix:** `/home/appfelix/claude/program_beli_padi/FASTAPI_UVICORN_FIX.md`

## Next Steps

After installation:
1. Setup PostgreSQL database (or use DEMO_MODE=true)
2. Run `python main.py`
3. Start creating purchase bills and delivery invoices!

## What's New in This Version

- **PyQt5-sip 12.13.0 explicitly specified** - No more build errors
- **No Visual C++ Build Tools required** - All packages use pre-built wheels
- **Comprehensive PyQt5 troubleshooting guide** - See PYQT5_WINDOWS7_INSTALL_GUIDE.md
- **All packages tested on Python 3.7.6 + Windows 7**
