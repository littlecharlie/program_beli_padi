# Build Quick Reference - Rice Billing System

**Windows 7 Compatible Executable**

---

## Prerequisites

```bash
# Python 3.8.10 required
python --version  # Should show Python 3.8.x

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller==5.13.2
```

---

## Build Commands

### Quick Build (Automated)
```bash
python build_executable.py --clean
```

### Manual Build
```bash
python create_icon.py              # Generate icon (first time only)
pyinstaller --clean rice_billing.spec
```

---

## Output Location

```
dist/RiceBillingSystem/
├── RiceBillingSystem.exe    ← Double-click to run
├── _internal/                ← Required libraries
└── ... other files
```

---

## Testing

### Demo Mode (No Database)
```bash
cd dist/RiceBillingSystem
copy .env.example .env
# Edit .env: Set DEMO_MODE=true
RiceBillingSystem.exe
```

### With Database
```bash
# Edit .env:
# DB_HOST=localhost
# DB_NAME=rice_billing_db
# DB_USER=postgres
# DB_PASSWORD=your_password
# DEMO_MODE=false
RiceBillingSystem.exe
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `pyinstaller` not found | `pip install pyinstaller==5.13.2` |
| Icon missing | `python create_icon.py` |
| Module not found | Add to `hiddenimports` in spec file |
| Build too slow | First build is ~5-10 min, normal |

---

## File Sizes

- **Executable:** ~150-200 MB (normal for PyQt5 app)
- **Total package:** ~150-200 MB
- **Startup:** 2-3 seconds (one-folder mode)

---

## Distribution

### Option 1: ZIP File
```bash
cd dist
zip -r RiceBillingSystem_v1.0.zip RiceBillingSystem/
```

### Option 2: Installer (Phase 3)
Use Inno Setup to create professional installer.
See `PHASE3_INSTALLER_CREATION.md`

---

## Next Steps

1. ✅ Build executable on Windows machine
2. ✅ Test in demo mode
3. ✅ Test with database
4. ✅ Test on Windows 7 VM
5. ⏭️ Proceed to Phase 3 (Installer)

---

**Need Help?** See `PHASE2_EXECUTABLE_CREATION.md` for detailed guide.
