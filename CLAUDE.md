# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Information

**GitHub Repository:** https://github.com/littlecharlie/program_beli_padi

Clone the repository:
```bash
git clone https://github.com/littlecharlie/program_beli_padi.git
cd program_beli_padi
```

## Project Overview

**Rice Billing System** - A Windows desktop application for managing rice purchase transactions and delivery invoices for AYOP BIN ARSHAD rice business in Sekinchan, Selangor. The system replaces an Excel-based workflow with a modern desktop application that prints receipts to an Epson LQ-310 dot matrix printer via USB.

**Tech Stack:**
- **Backend:** Python 3.10+, PostgreSQL, SQLAlchemy ORM, Alembic migrations
- **Desktop UI:** PyQt6 (primary choice)
- **Printing:** python-escpos for Epson LQ-310 dot matrix printer
- **Future Mobile:** FastAPI REST API with Flutter mobile client

## Key Architecture

### Core Structure

The application is organized into distinct layers:

1. **Database Layer** (`database/`, `models/`)
   - SQLAlchemy ORM models mirror the database schema
   - Alembic for schema migrations
   - Key models: `Farmer`, `PurchaseBill`, `DeliveryInvoice`, `RiceMill`, `Truck`, `HarvestArea`, `AuditLog`

2. **Service Layer** (`services/`)
   - **CalculationService:** All business calculations (discounts, net weight, payment, subsidy)
   - **PurchaseService:** Purchase bill CRUD and workflow
   - **DeliveryService:** Delivery invoice creation and bill grouping
   - **ConfigService:** Configuration management from database
   - **AuditService:** Audit trail tracking
   - Individual services for each entity (farmers, mills, trucks, areas)

3. **UI Layer** (`ui/`)
   - **Screens:** Dashboard, purchase entry, delivery entry, farmer/mill/truck management, reports, settings
   - **Widgets:** Reusable components (farmer selector, mill selector, bill/delivery tables)
   - **Dialogs:** Add/Edit/Confirm dialogs
   - **Styles:** QSS stylesheet definitions

4. **Printing Layer** (`printing/`)
   - **PrinterManager:** Manages Epson LQ-310 printer connections via USB
   - **EscposCommands:** Generates ESC/P commands for dot matrix printer
   - **Receipt Formatters:** Purchase bill and delivery invoice receipt formatters
   - **Templates:** Text-based receipt templates (Malay language)

### Database Schema Highlights

**Key Tables:**
- `config` - System configuration (rice price, discount defaults, company info)
- `farmers` - Farmer/supplier information
- `purchase_bills` - Individual purchase transactions with automatic numbering (13001+)
- `delivery_invoices` - Consolidated delivery invoices with automatic numbering (01001+)
- `delivery_items` - Junction table linking purchase bills to delivery invoices
- `rice_mills` - Rice mill destinations
- `trucks` - Truck information
- `harvest_areas` - Harvest area codes
- `audit_log` - Complete audit trail of all changes

**Auto-numbering Functions:**
- `get_next_bill_number()` - Returns next purchase bill number (13001, 13002, ...)
- `get_next_invoice_number()` - Returns next delivery invoice number (01001, 01002, ...)

**Important Views:**
- `vw_purchase_bills_full` - Purchase bills with all joined data
- `vw_delivery_invoices_full` - Delivery invoices with bill counts

### Core Business Logic

**Purchase Bill Workflow:**
1. Enter farmer IC number (with auto-lookup from database)
2. Select truck and enter gross weight
3. Set discount percentages (Wap Basah, Hampa Padi, Padi Muda/Rosak)
4. System automatically calculates:
   - Total discount percentage
   - Discount weight
   - Net weight = Gross weight - Discount weight
   - Total payment = (Net weight / 1000) × Price per 1000kg
   - Subsidy estimate = Net weight × RM 0.50/kg
5. Save and print receipt to Epson LQ-310

**Delivery Invoice Workflow:**
1. Select rice mill and truck
2. Select multiple purchase bills (checkboxes) not yet delivered
3. System calculates total weight
4. Create delivery invoice with auto-number
5. Mark all selected purchase bills as delivered
6. Print delivery invoice

**Key Calculations:** See `CalculationService` in specification for the exact logic.

## Development Commands

These commands will be commonly used:

### Database Setup

```bash
# Initialize database with schema
psql -U postgres -h localhost < RICE_BILLING_SYSTEM_SPECIFICATION.md

# Or use Alembic for migrations
alembic upgrade head

# Generate new migration after model changes
alembic revision --autogenerate -m "Description of changes"
```

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run desktop application
python main.py

# Run API server (for future mobile integration)
uvicorn api.main:app --reload
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov=models tests/

# Run specific test file
pytest tests/test_calculations.py -v

# Run single test
pytest tests/test_calculations.py::test_calculate_discount_weight -v
```

### Database Backup

```bash
# Automatic backup (handles cleanup of old backups)
python backup_database.py

# Manual pg_dump
pg_dump -h localhost -U postgres -F c -b -v -f backup_$(date +%Y%m%d_%H%M%S).sql rice_billing_db

# Restore from backup
pg_restore -h localhost -U postgres -d rice_billing_db backup_file.sql
```

## Common Development Tasks

### Adding a New Field to Purchase Bill

1. Update the model in `models/purchase_bill.py`
2. Create Alembic migration: `alembic revision --autogenerate -m "Add field_name to purchase_bills"`
3. Update UI in `ui/screens/purchase_entry.py` to display/input field
4. Update CalculationService if field affects calculations
5. Update receipt template in `printing/templates/purchase_template.txt` if needed
6. Add tests in `tests/test_calculations.py` if calculation affected

### Modifying Receipt Format

1. Edit the template file (`printing/templates/purchase_template.txt` or `delivery_template.txt`)
2. Test output width (Epson LQ-310 uses monospace, typically 80 columns)
3. Update receipt formatter class if formatting logic changed
4. Test actual print output to physical printer
5. Note: Receipts are in Malay language (BIL BELIAN, INVOIS HANTARAN, etc.)

### Adding New Discount Type

1. Add column to `purchase_bills` table via Alembic migration
2. Update `PurchaseBill` model
3. Add config entry to default discount percentage in `config` table
4. Update `CalculationService.calculate_purchase_bill()` method
5. Update purchase entry screen to display new discount field
6. Update receipt template

## Important Validations

The specification defines critical validation rules in `utils/validators.py`:

- **IC Number:** 12 digits, Malaysian format
- **Weight:** Must be > 0, max 1,000,000 kg
- **Percentage:** Must be 0-100, individual discounts constrained by checks
- **Phone:** Malaysian format (01X-XXXXXXX or 03-XXXXXXXX)
- **Date:** Cannot be in future
- **Net Weight Constraint:** Must equal `gross_weight - discount_weight` (enforced in database)

## Environment Configuration

Key `.env` variables that must be set:

```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rice_billing_db
DB_USER=postgres
DB_PASSWORD=

# Business configuration
DEFAULT_RICE_PRICE=1500.00           # Government price per 1000kg
DEFAULT_SUBSIDY_RATE=0.50            # Subsidy rate per kg
DEFAULT_DISCOUNT_WAP_BASAH=7.00      # Moisture discount %
DEFAULT_DISCOUNT_HAMPA_PADI=7.00     # Empty grains discount %
DEFAULT_DISCOUNT_PADI_MUDA=6.00      # Damaged rice discount %

# Printer
PRINTER_NAME=EPSON LQ-310
PRINTER_INTERFACE=usb
```

## Auto-numbering System

**Purchase Bill Numbers:** Start at 13001, increment by 1
- Format: 5-digit numeric string (13001, 13002, ...)
- Generated by `get_next_bill_number()` PostgreSQL function
- Must be unique in database

**Delivery Invoice Numbers:** Start at 01001, increment by 1
- Format: 5-digit zero-padded numeric string (01001, 01002, ...)
- Generated by `get_next_invoice_number()` PostgreSQL function
- Must be unique in database

## Key Business Rules

1. **Purchase bills can only be delivered once** - `is_delivered` boolean tracks this
2. **Delivery invoices contain multiple purchase bills** - junction table `delivery_items` manages this
3. **Total discount cannot exceed 100%** - enforced by database CHECK constraint
4. **Net weight calculation is fixed** - `net_weight = gross_weight - discount_weight` (database constraint)
5. **Farmer cannot be deleted if they have purchase bills** - foreign key ON DELETE RESTRICT
6. **Audit trail required** - all changes to farmers, purchase bills, delivery invoices logged automatically
7. **Configuration is dynamic** - all business parameters stored in `config` table, not hardcoded

## Testing Strategy

From specification, focus testing on:

1. **Unit Tests** (`tests/test_calculations.py`)
   - CalculationService methods with exact examples from spec
   - Validators for all input types
   - Edge cases (0 weight, 100% discount, boundary values)

2. **Integration Tests** (`tests/test_services.py`)
   - Complete purchase bill creation workflow
   - Complete delivery invoice creation workflow
   - Farmer CRUD operations
   - Database constraints work correctly

3. **Manual Testing**
   - Actual printing to Epson LQ-310 printer
   - Complete user workflows (purchase → delivery)
   - UI responsiveness and data binding

## Receipt Formatting

**Critical for Epson LQ-310:**
- Use monospace characters only
- Line width: 80 columns max
- ESC/P commands for formatting (bold, underline, centering)
- Character-based (not pixel) printing
- Must match sample formats shown in specification
- All text in Malay (BIL BELIAN, INVOIS HANTARAN, etc.)

## Troubleshooting Notes

- **Database connection issues:** Check PostgreSQL service and credentials in `.env`
- **Printer not found:** Verify USB connection, printer powered on, driver installed
- **Calculation mismatches:** Verify discount sum doesn't exceed 100%, check rounding (2 decimal places)
- **Cannot create delivery invoice:** All selected bills must be from same mill, not already delivered

## Dependencies Overview

- **psycopg2-binary:** PostgreSQL adapter for Python
- **sqlalchemy:** ORM for database operations
- **alembic:** Database migration tool
- **PyQt6:** Desktop UI framework
- **python-escpos:** Epson ESC/P printer commands
- **pywin32:** Windows printer integration
- **fastapi/uvicorn:** Future API server for mobile app
- **pytest:** Testing framework
