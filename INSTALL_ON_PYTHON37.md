# Quick Installation Guide - Python 3.7.6

## Prerequisites

- **Python 3.7.6** installed on Windows 7
- **PostgreSQL** database installed
- **pip** package manager

---

## Installation Steps

### 1. Upgrade pip (Important!)

```bash
python -m pip install --upgrade pip==23.0.1
pip install setuptools==59.6.0 wheel
```

### 2. Install Dependencies

```bash
pip install -r requirements-python37.txt
```

If you see errors about missing Visual C++, download and install:
**Microsoft Visual C++ 14.0 Build Tools** from Microsoft's website.

### 3. Configure Environment

Create a `.env` file in the project root:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rice_billing_db
DB_USER=postgres
DB_PASSWORD=your_password

# Business configuration
DEFAULT_RICE_PRICE=1500.00
DEFAULT_SUBSIDY_RATE=0.50
DEFAULT_DISCOUNT_WAP_BASAH=7.00
DEFAULT_DISCOUNT_HAMPA_PADI=7.00
DEFAULT_DISCOUNT_PADI_MUDA=6.00

# Printer
PRINTER_NAME=EPSON LQ-310
PRINTER_INTERFACE=usb
```

### 4. Initialize Database

```bash
# Option A: Using SQL script
psql -U postgres -h localhost < RICE_BILLING_SYSTEM_SPECIFICATION.md

# Option B: Using Alembic
alembic upgrade head
```

### 5. Run the Application

```bash
python main.py
```

---

## Troubleshooting

### Problem: "No module named 'PyQt5'"
**Solution:**
```bash
pip install PyQt5==5.15.10
```

### Problem: "Could not find a version that satisfies the requirement..."
**Solution:** Make sure you're using Python 3.7.6:
```bash
python --version
# Should output: Python 3.7.6
```

### Problem: "error: Microsoft Visual C++ 14.0 is required"
**Solution:** Install Microsoft C++ Build Tools or use pre-built wheels:
```bash
pip install --only-binary :all: -r requirements-python37.txt
```

### Problem: Database connection errors
**Solution:** Check PostgreSQL is running and credentials in `.env` are correct:
```bash
# Test PostgreSQL connection
psql -U postgres -h localhost -c "SELECT version();"
```

---

## Verify Installation

Run these tests to verify everything works:

```bash
# 1. Test imports
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
python -c "from sqlalchemy import create_engine; print('SQLAlchemy OK')"
python -c "import psycopg2; print('PostgreSQL OK')"

# 2. Run tests
pytest -v

# 3. Test application launch
python main.py
```

---

## Common Issues on Windows 7

### Issue: SSL Certificate Errors
Add to pip.ini (create in `%APPDATA%\pip\pip.ini`):
```ini
[global]
trusted-host = pypi.org
               files.pythonhosted.org
```

### Issue: TLS/SSL Version Errors
Upgrade pip's dependencies:
```bash
python -m pip install --upgrade pip certifi urllib3
```

---

## Package Versions (All Python 3.7 Compatible)

| Package | Version | Notes |
|---------|---------|-------|
| PyQt5 | 5.15.10 | Last version for Windows 7 |
| SQLAlchemy | 1.4.53 | Transition version (1.x/2.0 compatible) |
| alembic | 1.12.1 | Database migrations |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| reportlab | 3.6.13 | PDF generation |
| Pillow | 9.5.0 | Image processing |
| pytest | 7.4.3 | Testing framework |

---

## Next Steps After Installation

1. **Configure printer** - Connect Epson LQ-310 via USB
2. **Import initial data** - Add farmers, mills, trucks
3. **Test receipt printing** - Print a test purchase bill
4. **Backup database** - Run `python backup_database.py`

---

## Getting Help

- Check `PYTHON37_FIX_COMPLETE.md` for detailed changes
- Check `PYTHON37_CHANGES_SUMMARY.txt` for quick reference
- Review error messages carefully - they often indicate missing dependencies

---

**Installation should now work without the alembic version error!** ✅
