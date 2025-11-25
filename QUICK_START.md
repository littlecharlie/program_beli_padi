# Quick Start - Run the Application

## Prerequisites

- Python 3.10+
- pip (Python package manager)

## Installation & Running (5 minutes)

### 1. Install Dependencies

```bash
pip install PyQt6 sqlalchemy psycopg2-binary python-dotenv
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Run in Demo Mode (No Database Needed)

```bash
DEMO_MODE=true python main.py
```

Or on Windows:
```cmd
set DEMO_MODE=true
python main.py
```

This will launch the application with a sample dashboard showing demo data. All UI elements are interactive and functional for testing.

### 3. Run with Real Database (Optional)

First, set up PostgreSQL:
```bash
# Create database
psql -U postgres
CREATE DATABASE rice_billing_db;
GRANT ALL PRIVILEGES ON DATABASE rice_billing_db TO postgres;
\q

# Edit .env and set DEMO_MODE=false

# Run the app
python main.py
```

## What You'll See

When you run the app, you'll get:
- ✅ Main application window with navigation buttons
- ✅ Dashboard screen with statistics cards
- ✅ Sample data showing purchase bills, deliveries, and farmer counts
- ✅ Quick action buttons for testing navigation
- ✅ Professional UI with color-coded information

## Features Available in Demo Mode

- Dashboard with statistics cards
- Sample data for all metrics
- Interactive navigation buttons
- Professional UI styling
- Demo mode indicator dialog

## Features Requiring Database

Once you set up PostgreSQL and disable demo mode:
- Purchase bill creation and management
- Delivery invoice generation
- Farmer/Mill/Truck management
- Report generation
- Receipt printing

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt6'"
```bash
pip install PyQt6
```

### Window doesn't appear
- On Linux/Mac with display issues, you may need X11 forwarding
- The application requires a display server

### Database connection error
- This is expected in demo mode
- Set `DEMO_MODE=true` in .env or via environment variable

## Next Steps

1. Run the app and explore the UI
2. Click navigation buttons to see different screens
3. When ready, set up PostgreSQL for full functionality
4. See RUN_INSTRUCTIONS.md for detailed setup guide
5. See CLAUDE.md for architecture and development info

---

**That's it! Enjoy exploring the Rice Billing System!**

🤖 Built with Claude Code
