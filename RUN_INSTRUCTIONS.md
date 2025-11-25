# Rice Billing System - How to Run

## Quick Start (Demo Mode - No Database Required)

This is the easiest way to test the UI without setting up PostgreSQL.

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Steps

1. **Navigate to project directory:**
   ```bash
   cd program_beli_padi
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run in demo mode:**
   ```bash
   python main.py
   ```

   The application will start with a demo mode notification showing that the database is not connected. All UI elements will be functional for testing.

---

## Full Setup (With PostgreSQL Database)

For production use with actual data storage.

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- pip

### Steps

1. **Install PostgreSQL** (if not already installed)
   - Windows: Download from https://www.postgresql.org/download/windows/
   - macOS: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql postgresql-contrib`

2. **Start PostgreSQL service:**
   - Windows: Start PostgreSQL service from Services
   - macOS: `brew services start postgresql`
   - Linux: `sudo systemctl start postgresql`

3. **Create database and user:**
   ```bash
   psql -U postgres

   # In PostgreSQL prompt:
   CREATE DATABASE rice_billing_db;
   CREATE USER postgres WITH PASSWORD 'postgres';
   ALTER ROLE postgres SET client_encoding TO 'utf8';
   ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
   ALTER ROLE postgres SET default_transaction_deferrable TO on;
   GRANT ALL PRIVILEGES ON DATABASE rice_billing_db TO postgres;
   \q
   ```

4. **Navigate to project directory:**
   ```bash
   cd program_beli_padi
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Disable demo mode in .env:**
   Edit `.env` and set:
   ```
   DEMO_MODE=false
   ```

7. **Run the application:**
   ```bash
   python main.py
   ```

   The application will connect to PostgreSQL and initialize the database.

---

## Project Structure

```
program_beli_padi/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Configuration file
├── CLAUDE.md              # Development guide
├── config/                # Configuration modules
├── database/              # Database connection and initialization
├── models/                # SQLAlchemy ORM models
├── services/              # Business logic services
├── ui/                    # PyQt6 user interface
│   ├── main_window.py     # Main window
│   ├── screens/           # Screen implementations
│   │   ├── dashboard.py
│   │   ├── purchase_entry.py
│   │   ├── purchase_list.py
│   │   ├── delivery_entry.py
│   │   ├── delivery_list.py
│   │   ├── master_data.py
│   │   ├── reports.py
│   │   └── settings.py
│   ├── widgets/           # Reusable UI widgets
│   └── styles.py          # QSS stylesheets
├── printing/              # Receipt printing
│   ├── templates/         # Receipt templates
│   ├── escpos_commands.py # Printer commands
│   └── formatters/        # Receipt formatters
└── utils/                 # Utility functions
```

---

## Features

### Phase 1: Foundation ✅
- Database schema with 9 tables
- SQLAlchemy ORM models
- CRUD services for all entities
- PyQt6 UI framework

### Phase 2: Purchase Bills ✅
- Create and manage purchase bills
- Auto-calculations (discount, net weight, payment)
- Receipt printing (Malay language)
- Bill listing with search/filter

### Phase 3: Delivery Invoices ✅
- Create delivery invoices with bill grouping
- Auto-numbering system
- Delivery receipt printing
- Invoice listing with search/filter

### Phase 4: Reports & Management ✅
- Dashboard with statistics
- Master data management (Farmers, Mills, Trucks)
- Multi-type reporting with filtering
- Configuration management screen

---

## Configuration

Edit `.env` to configure:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rice_billing_db
DB_USER=postgres
DB_PASSWORD=postgres

# Demo mode (set to false for real database)
DEMO_MODE=true

# Business settings
DEFAULT_RICE_PRICE=1500.00
DEFAULT_SUBSIDY_RATE=0.50
DEFAULT_DISCOUNT_WAP_BASAH=7.00
DEFAULT_DISCOUNT_HAMPA_PADI=7.00
DEFAULT_DISCOUNT_PADI_MUDA=6.00

# Company information
COMPANY_NAME=AYOP BIN ARSHAD
COMPANY_ADDRESS_1=LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR
COMPANY_PHONE=0162120051
COMPANY_MANAGER=AH SENG
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt6'"
- Install dependencies: `pip install -r requirements.txt`
- Use Python 3.10+: `python3 --version`

### "DatabaseError: Connection failed"
- Ensure PostgreSQL is running
- Check .env database credentials
- Or use demo mode: Set `DEMO_MODE=true`

### "Cannot connect to printer"
- Printer integration is optional
- App works fine without printer in demo mode
- For actual printing, ensure Epson LQ-310 is connected via USB

### UI looks wrong or doesn't render
- Ensure PyQt6 and all dependencies are installed
- Try updating: `pip install --upgrade -r requirements.txt`

---

## Development

For development tasks, see `CLAUDE.md` for:
- Architecture overview
- Development commands
- Testing guide
- Common development tasks

---

## License & Attribution

Rice Billing System for AYOP BIN ARSHAD
Sekinchan, Selangor, Malaysia

🤖 Generated with Claude Code
