# PyQt5 Windows 7 Installation - Quick Fix

## The Problem
```
error: Microsoft Visual C++ 14.0 or greater is required
ERROR: Failed building wheel for PyQt5-sip
```

## The Solution (30 seconds)

### Option 1: Use Updated Requirements File (RECOMMENDED)
```bash
pip install -r requirements-python37.txt
```

The file now includes `PyQt5-sip==12.13.0` with pre-built wheels. Done!

### Option 2: Manual Installation
```bash
pip install PyQt5-sip==12.13.0
pip install PyQt5==5.15.10
```

Order matters! PyQt5-sip must come first.

### Option 3: Clear Cache and Reinstall
```bash
pip cache purge
pip uninstall PyQt5 PyQt5-sip -y
pip install PyQt5-sip==12.13.0 PyQt5==5.15.10
```

## Verify It Works
```bash
python -c "from PyQt5.QtWidgets import QApplication; print('Success!')"
```

## Still Having Issues?

See comprehensive guide: [PYQT5_WINDOWS7_INSTALL_GUIDE.md](PYQT5_WINDOWS7_INSTALL_GUIDE.md)

## Why This Works

- PyQt5-sip 12.13.0 has pre-built wheels for Python 3.7 on Windows
- No compilation needed
- No Visual C++ Build Tools required
- Just downloads and installs the wheel

## The Key Rule

**Always specify PyQt5-sip explicitly BEFORE PyQt5 in requirements.txt**

```txt
# Good (works)
PyQt5-sip==12.13.0
PyQt5==5.15.10

# Bad (fails)
PyQt5==5.15.10
# pip auto-selects wrong PyQt5-sip version
```

---

That's it! Installation should now work smoothly on Windows 7 with Python 3.7.6.
