@echo off
REM ========================================
REM Rice Billing System - Windows 7 Installer
REM Python 3.7.6 Compatible
REM ========================================

echo.
echo ========================================
echo Rice Billing System Installation
echo Windows 7 + Python 3.7.6
echo ========================================
echo.

REM Check Python version
echo [1/5] Checking Python version...
python --version 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.7.6 from:
    echo https://www.python.org/ftp/python/3.7.6/python-3.7.6-amd64.exe
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

python --version | findstr "3.7" >nul
if %errorlevel% neq 0 (
    echo [WARNING] You are not using Python 3.7.x
    echo This application is designed for Python 3.7.6
    echo.
    python --version
    echo.
    echo Continue anyway? (Press Ctrl+C to cancel, or any key to continue)
    pause >nul
)

echo [OK] Python detected
echo.

REM Upgrade pip
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip==23.0.1 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Could not upgrade pip, continuing with current version
)
echo.

REM Install setuptools and wheel
echo [3/5] Installing build tools...
pip install setuptools==59.6.0 wheel 2>nul
echo.

REM Install dependencies
echo [4/5] Installing dependencies from requirements-python37.txt...
echo This may take several minutes...
echo.
pip install -r requirements-python37.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    echo Common solutions:
    echo 1. Make sure you have internet connection
    echo 2. Try running this script as Administrator
    echo 3. Install Microsoft Visual C++ 14.0 Build Tools
    echo.
    pause
    exit /b 1
)

echo.
echo [5/5] Verifying installation...
python -c "import PyQt5; print('[OK] PyQt5')" 2>nul
python -c "import sqlalchemy; print('[OK] SQLAlchemy')" 2>nul
python -c "import psycopg2; print('[OK] PostgreSQL driver')" 2>nul
python -c "from escpos.printer import Usb; print('[OK] ESC/POS printer support')" 2>nul

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure PostgreSQL is installed and running
echo 2. Create a .env file with your database credentials
echo 3. Initialize the database: alembic upgrade head
echo 4. Run the application: python main.py
echo.
echo For help, see: INSTALL_ON_PYTHON37.md
echo.
pause
