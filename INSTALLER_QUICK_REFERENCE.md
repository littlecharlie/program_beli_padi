# Installer Quick Reference - Rice Billing System

**Professional Windows Installer Creation**

---

## Prerequisites

```bash
# 1. Executable must be built first
python build_executable.py --clean

# 2. Install Inno Setup 6
# Download from: https://jrsoftware.org/isinfo.php
```

---

## Build Installer (One Command)

```bash
python build_installer.py --clean
```

**Output:**
```
installer_output/RiceBillingSystem_Setup_v1.0.0.exe
```

---

## Installation Flow

User downloads `RiceBillingSystem_Setup_v1.0.0.exe` and runs it:

1. **Welcome** → Shows app info
2. **License** → User accepts
3. **Info** → Requirements and notices
4. **Folder** → Choose install location
5. **Components** → Select features
6. **Database Config** → Choose mode:
   - **Database Mode** → Enter PostgreSQL credentials
   - **Demo Mode** → No database needed
7. **Install** → Copies files, creates shortcuts
8. **Finish** → Launch app

---

## What Gets Installed

```
C:\Program Files\Rice Billing System\
├── RiceBillingSystem.exe    ← Main app
├── .env                      ← Auto-created by installer
├── scripts/                  ← Helper scripts
└── ... all other files

Desktop\
└── Rice Billing System.lnk   ← Shortcut with icon

Start Menu\Rice Billing System\
├── Rice Billing System
├── Configure Database
├── User Guide
└── Uninstall
```

---

## Testing Checklist

### Demo Mode Test
- [ ] Install in Demo Mode
- [ ] Launch application
- [ ] Verify runs without database
- [ ] Uninstall cleanly

### Database Mode Test
- [ ] Install PostgreSQL
- [ ] Install in Database Mode
- [ ] Enter correct credentials
- [ ] Launch application
- [ ] Create test data
- [ ] Verify data persists
- [ ] Uninstall (data preserved)

---

## Common Issues

| Problem | Solution |
|---------|----------|
| Inno Setup not found | Install from jrsoftware.org |
| Executable missing | Run `build_executable.py` first |
| Compilation error | Check all files in `installer/` exist |
| Won't run on Win7 | Need Windows 7 SP1 + .NET 4.5+ |

---

## File Sizes

- **Installer:** ~150-200 MB
- **Installed:** ~150-200 MB
- **Compression:** LZMA2 (maximum)

---

## Advanced Usage

### Silent Installation
```bash
Setup.exe /SILENT         # No UI
Setup.exe /VERYSILENT     # No UI, no progress
```

### Custom Install Path
```bash
Setup.exe /DIR="D:\MyApps\RiceBilling"
```

### Enable Installation Log
```bash
Setup.exe /LOG="C:\install.log"
```

---

## Distribution Methods

1. **Direct Download** - Host on website
2. **USB Drive** - Copy installer to USB
3. **Network Share** - Place on company server

---

**Need Help?** See `PHASE3_INSTALLER_CREATION.md` for detailed guide.
