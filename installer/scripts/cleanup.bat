@echo off
REM Rice Billing System - Uninstallation Cleanup Script
REM This script runs before uninstallation to clean up temporary files

echo Rice Billing System - Cleanup
echo ==============================
echo.

REM Delete log files
if exist "*.log" (
    echo Deleting log files...
    del /Q "*.log" 2>nul
)

REM Delete Python cache
if exist "__pycache__" (
    echo Removing Python cache...
    rmdir /S /Q "__pycache__" 2>nul
)

REM Delete temporary files
if exist "temp" (
    echo Removing temporary files...
    rmdir /S /Q "temp" 2>nul
)

REM Note: We do NOT delete:
REM - .env file (user configuration)
REM - exports/ folder (user data)
REM - backups/ folder (user data)
REM - Database (stored in PostgreSQL)
REM
REM These can be manually deleted by the user if desired

echo.
echo Cleanup complete
exit /b 0
