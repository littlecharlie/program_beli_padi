# PyQt5 Installation Guide for Windows 7 with Python 3.7.6

## Problem Overview

When installing PyQt5 on Windows 7 with Python 3.7.6, you may encounter this error:

```
Building wheel for PyQt5-sip (pyproject.toml) ... error
error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools"
ERROR: Failed building wheel for PyQt5-sip
```

**Root Cause:** PyQt5-sip tries to build from source when a compatible pre-built wheel is not found, requiring Microsoft Visual C++ Build Tools which may not be available on Windows 7.

## Solution

### Primary Fix (RECOMMENDED)

The `requirements-python37.txt` file has been updated to explicitly specify PyQt5-sip version with pre-built wheels:

```txt
PyQt5-sip==12.13.0  # Must come BEFORE PyQt5
PyQt5==5.15.10
```

**Why this works:**
- PyQt5-sip 12.13.0 has pre-built wheels for `cp37-win_amd64` (Python 3.7 on Windows 64-bit)
- Installing PyQt5-sip explicitly before PyQt5 prevents pip from trying to build it from source
- No compiler required

### Installation Steps

1. **Create a virtual environment** (recommended):
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Upgrade pip, setuptools, and wheel**:
   ```cmd
   python -m pip install --upgrade pip setuptools wheel
   ```

3. **Install from requirements**:
   ```cmd
   pip install -r requirements-python37.txt
   ```

4. **Verify installation**:
   ```cmd
   python -c "import PyQt5; print(PyQt5.__version__)"
   python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
   ```

## Alternative Solutions (If Primary Fix Fails)

### Option A: Install PyQt5-sip Separately First

```cmd
pip install PyQt5-sip==12.13.0
pip install PyQt5==5.15.10
pip install -r requirements-python37.txt
```

### Option B: Use Older PyQt5 Version

If PyQt5 5.15.10 still has issues, try PyQt5 5.15.6 or 5.15.7:

```cmd
pip install PyQt5-sip==12.11.0
pip install PyQt5==5.15.6
```

### Option C: Use Pre-built PyQt5 Binary Package

Download and install from unofficial Windows binaries (Christoph Gohlke's collection):
- Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/
- Download: `PyQt5‑5.15.X‑cp37‑cp37m‑win_amd64.whl`
- Install: `pip install PyQt5‑5.15.X‑cp37‑cp37m‑win_amd64.whl`

### Option D: Install Visual C++ Build Tools (Last Resort)

Only if none of the above work:

1. Download Microsoft Visual C++ 14.0 Build Tools
2. Install with "Desktop development with C++" workload
3. Try installing again with original requirements

**Warning:** This is 3-4 GB download and may not be ideal for Windows 7 systems.

## Troubleshooting

### Error: "Could not find a version that satisfies the requirement"

This means pip cannot find a compatible wheel. Try:

```cmd
# Update pip first
python -m pip install --upgrade pip

# Try installing with verbose output
pip install PyQt5-sip==12.13.0 -v
```

### Error: "No matching distribution found for PyQt5-sip==12.13.0"

Your pip may be outdated or using wrong Python version. Verify:

```cmd
python --version  # Should show Python 3.7.6
pip --version     # Should show pip for Python 3.7
```

### Error: DLL load failed

This typically happens after installation if dependencies are missing:

```cmd
# Reinstall with no cache
pip uninstall PyQt5 PyQt5-sip -y
pip install --no-cache-dir PyQt5-sip==12.13.0 PyQt5==5.15.10
```

## Version Compatibility Matrix

| Python Version | PyQt5 Version | PyQt5-sip Version | Pre-built Wheel? |
|----------------|---------------|-------------------|------------------|
| 3.7.6          | 5.15.10       | 12.13.0           | Yes (cp37-win_amd64) |
| 3.7.6          | 5.15.9        | 12.12.2           | Yes (cp37-win_amd64) |
| 3.7.6          | 5.15.7        | 12.11.0           | Yes (cp37-win_amd64) |
| 3.7.6          | 5.15.6        | 12.11.0           | Yes (cp37-win_amd64) |

## Why PyQt5-sip Must Come Before PyQt5

When you specify only `PyQt5==5.15.10`, pip:
1. Downloads PyQt5 5.15.10
2. Reads its dependencies (requires PyQt5-sip ~=12.13)
3. Tries to find PyQt5-sip 12.13.x
4. May select a version that requires compilation
5. Tries to build from source → ERROR

When you specify `PyQt5-sip==12.13.0` first:
1. pip downloads the pre-built wheel for PyQt5-sip 12.13.0
2. Installs it successfully
3. Then installs PyQt5 5.15.10
4. PyQt5's dependency on PyQt5-sip is already satisfied → SUCCESS

## Testing PyQt5 Installation

Create a test file `test_pyqt5.py`:

```python
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

def test_pyqt5():
    print(f"Creating QApplication...")
    app = QApplication(sys.argv)

    print(f"Creating QMainWindow...")
    window = QMainWindow()
    window.setWindowTitle("PyQt5 Test - Windows 7 Compatible")
    window.setGeometry(100, 100, 400, 200)

    print(f"Creating QLabel...")
    label = QLabel("PyQt5 is working on Windows 7 with Python 3.7.6!", window)
    label.setGeometry(50, 80, 300, 30)

    print(f"Showing window...")
    window.show()

    print("PyQt5 installation successful!")
    print(f"PyQt5 version: {__import__('PyQt5.Qt', fromlist=['PYQT_VERSION_STR']).PYQT_VERSION_STR}")

    # Close after 2 seconds
    import threading
    def close_app():
        import time
        time.sleep(2)
        app.quit()

    threading.Thread(target=close_app, daemon=True).start()

    return app.exec_()

if __name__ == "__main__":
    test_pyqt5()
```

Run it:
```cmd
python test_pyqt5.py
```

If a window appears with the text, PyQt5 is working correctly!

## Additional Notes

### Why Not PyQt6?

PyQt6 requires Python 3.6.1+ but has issues with Windows 7:
- Windows 7 is not officially supported by Qt6
- Missing Windows API functions that Qt6 depends on
- PyQt5 is the recommended version for Windows 7 compatibility

### Cache Issues

If you're switching between different PyQt5 versions, always clear pip cache:

```cmd
pip cache purge
pip uninstall PyQt5 PyQt5-sip -y
pip install --no-cache-dir -r requirements-python37.txt
```

### Virtual Environment Recommended

Always use a virtual environment to avoid conflicts:

```cmd
# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Deactivate (when done)
deactivate
```

## Support

If you continue to have issues:

1. Check Python version: `python --version` (should be 3.7.6)
2. Check pip version: `pip --version` (should be 20.0+)
3. Verify Windows architecture: `python -c "import platform; print(platform.machine())"` (should be AMD64)
4. Try the alternative solutions above in order
5. Share full error output for debugging

## References

- PyPI PyQt5: https://pypi.org/project/PyQt5/
- PyPI PyQt5-sip: https://pypi.org/project/PyQt5-sip/
- Riverbank Computing (PyQt5 developers): https://www.riverbankcomputing.com/
- Unofficial Windows binaries: https://www.lfd.uci.edu/~gohlke/pythonlibs/
