# Rice Billing System - Complete Project Specification

## Project Overview

A Windows desktop application for managing rice purchase transactions and delivery invoices for **AYOP BIN ARSHAD** rice business in Sekinchan, Selangor. The system replaces an Excel-based workflow with a modern desktop application that prints receipts to an Epson LQ-310 dot matrix printer via USB.

**Business:** Rice purchasing from farmers and consolidated delivery to rice mills  
**Future Expansion:** Mobile app using Flutter to connect to desktop database

---

## Business Workflow

### Current Process

1. **Individual Purchase (BIL BELIAN PADI)**
   - Farmer brings rice (padi) to buyer
   - Rice is weighed on weighbridge (gross weight)
   - Discounts applied for moisture, empty grains, damaged rice
   - Net weight calculated
   - Payment calculated based on government price (RM 1,500 per 1000kg)
   - Subsidy estimated (net weight × RM 0.50)
   - Individual purchase receipt printed

2. **Consolidated Delivery (INVOIS HANTARAN)**
   - Multiple farmers' rice loaded onto same truck
   - All going to same rice mill
   - Single delivery invoice created
   - Lists all farmers and their rice weight on this delivery
   - Consolidated receipt printed

### Sample Calculations

**Purchase Bill Example:**
```
Gross Weight:        6,680.00 kg
Discounts:
  - Wap Basah:       7%
  - Hampa Padi:      7%
  - Padi Muda/Rosak: 6%
  - Total:           20%

Discount Weight:     1,336.00 kg (6,680 × 20%)
Net Weight:          5,344.00 kg
Price:               RM 1,500.00 per 1000kg
Total Payment:       RM 8,016.00 (5,344 ÷ 1000 × 1,500)
Subsidy Estimate:    RM 2,672.00 (5,344 × 0.50)
```

**Delivery Invoice Example:**
```
Invoice: 01876
Mill: KILANG BERAS RAKYAT SEKINCHAN
Truck: WDP 7349

Bills Included:
  13096 - MOHD FUAD BIN ARSHAD       - 9,230 kg
  13097 - SITI FITRIYATULAKMAL       - 4,300 kg
  13098 - ABDULLAH BIN IBAK          - 7,610 kg
  13099 - SATAR BIN TALIP            - 1,200 kg
  13100 - ISMAIL BIN ABUT            - 1,330 kg
  
Total Weight:                        23,670 kg
```

---

## Technology Stack

### Backend/Core
- **Python:** 3.10+
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic

### Desktop UI
- **Framework:** PyQt6 (recommended) or Tkinter
- **Printing:** python-escpos for Epson LQ-310
- **Printer Communication:** pywin32 for Windows printer access

### Future Mobile
- **Flutter:** Cross-platform mobile app
- **API:** FastAPI REST API
- **Architecture:** Desktop as server, mobile as client

---

## Database Schema

### Complete PostgreSQL Schema

```sql
-- ============================================
-- CONFIGURATION TABLE
-- ============================================
CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial config data
INSERT INTO config (key, value, description) VALUES
('rice_price_per_1000kg', '1500.00', 'Government-set rice price per 1000kg'),
('discount_wap_basah_default', '7.00', 'Default moisture discount percentage'),
('discount_hampa_padi_default', '7.00', 'Default empty grains discount percentage'),
('discount_padi_muda_default', '6.00', 'Default damaged rice discount percentage'),
('subsidy_rate', '0.50', 'Subsidy calculation rate per kg'),
('company_name', 'AYOP BIN ARSHAD', 'Company name'),
('company_address', 'LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR', 'Company address'),
('company_address_2', 'SELANGOR DARUL EHSAN', 'Company address line 2'),
('company_registration', '474523-K', 'Business registration number'),
('company_phone', '0162120051', 'Company phone number'),
('manager_name', 'AH SENG', 'Manager name');

-- ============================================
-- FARMERS/SUPPLIERS TABLE
-- ============================================
CREATE TABLE farmers (
    id SERIAL PRIMARY KEY,
    ic_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    registration_number VARCHAR(50),  -- NO DAFTAR PESAWAH (B002/11/25)
    subsidy_code VARCHAR(50),         -- NO KAD SUBSIDI
    bank_account VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO farmers (ic_number, name, registration_number, address) VALUES
('710502105256', 'RUSIDAH BINTI ARDI', 'B002/11/25', '0');

-- ============================================
-- RICE MILLS TABLE
-- ============================================
CREATE TABLE rice_mills (
    id SERIAL PRIMARY KEY,
    mill_code VARCHAR(10) UNIQUE NOT NULL,  -- A1, A2, A3, etc.
    mill_name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO rice_mills (mill_code, mill_name) VALUES
('A1', 'BERNAS SRI TIRAM JAYA'),
('A2', 'BERNAS SEKINCHAN'),
('A4', 'HAYAT MAJU'),
('A5', 'LIM SEKINCHAN'),
('A6', 'PEKET 60'),
('A7', 'FIRMA RENA'),
('A8', 'DATARAN'),
('A9', 'KILANG BERAS RAKYAT SEKINCHAN');

-- ============================================
-- TRUCKS TABLE
-- ============================================
CREATE TABLE trucks (
    id SERIAL PRIMARY KEY,
    truck_number VARCHAR(20) UNIQUE NOT NULL,
    tare_weight DECIMAL(10,2),  -- Optional
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO trucks (truck_number, tare_weight) VALUES
('WDP 7349', 0),
('BDP/WES', NULL);

-- ============================================
-- HARVEST AREAS TABLE
-- ============================================
CREATE TABLE harvest_areas (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO harvest_areas (area_name) VALUES
('PASIR PANJANG');

-- ============================================
-- PURCHASE BILLS (BIL BELIAN PADI)
-- ============================================
CREATE TABLE purchase_bills (
    id SERIAL PRIMARY KEY,
    bill_number VARCHAR(20) UNIQUE NOT NULL,  -- 13096, 13097, 13098...
    farmer_id INTEGER REFERENCES farmers(id) ON DELETE RESTRICT,
    bill_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Weighing information
    truck_id INTEGER REFERENCES trucks(id) ON DELETE RESTRICT,
    weighbridge_receipt VARCHAR(50),  -- NO RESIT TIMBANG (017084)
    gross_weight DECIMAL(10,2) NOT NULL CHECK (gross_weight > 0),
    
    -- Discount percentages
    discount_wap_basah DECIMAL(5,2) DEFAULT 7.00 CHECK (discount_wap_basah >= 0 AND discount_wap_basah <= 100),
    discount_hampa_padi DECIMAL(5,2) DEFAULT 7.00 CHECK (discount_hampa_padi >= 0 AND discount_hampa_padi <= 100),
    discount_padi_muda DECIMAL(5,2) DEFAULT 6.00 CHECK (discount_padi_muda >= 0 AND discount_padi_muda <= 100),
    total_discount_percent DECIMAL(5,2) NOT NULL CHECK (total_discount_percent >= 0 AND total_discount_percent <= 100),
    
    -- Calculated weights
    discount_weight DECIMAL(10,2) NOT NULL CHECK (discount_weight >= 0),
    net_weight DECIMAL(10,2) NOT NULL CHECK (net_weight > 0),
    
    -- Payment calculations
    rice_price_per_1000kg DECIMAL(10,2) NOT NULL,
    total_payment DECIMAL(10,2) NOT NULL CHECK (total_payment >= 0),
    subsidy_estimate DECIMAL(10,2) NOT NULL CHECK (subsidy_estimate >= 0),
    
    -- Additional information
    harvest_area_id INTEGER REFERENCES harvest_areas(id) ON DELETE SET NULL,
    
    -- Status tracking
    is_delivered BOOLEAN DEFAULT FALSE,
    delivery_invoice_id INTEGER,  -- Will reference delivery_invoices(id)
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    
    CONSTRAINT chk_net_weight CHECK (net_weight = gross_weight - discount_weight)
);

-- ============================================
-- DELIVERY INVOICES (INVOIS HANTARAN)
-- ============================================
CREATE TABLE delivery_invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(20) UNIQUE NOT NULL,  -- 01876, 01877...
    invoice_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    mill_id INTEGER REFERENCES rice_mills(id) ON DELETE RESTRICT,
    truck_id INTEGER REFERENCES trucks(id) ON DELETE RESTRICT,
    
    total_weight DECIMAL(10,2) NOT NULL CHECK (total_weight > 0),
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- ============================================
-- DELIVERY ITEMS (Link purchase bills to delivery invoices)
-- ============================================
CREATE TABLE delivery_items (
    id SERIAL PRIMARY KEY,
    delivery_invoice_id INTEGER REFERENCES delivery_invoices(id) ON DELETE CASCADE,
    purchase_bill_id INTEGER REFERENCES purchase_bills(id) ON DELETE RESTRICT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(delivery_invoice_id, purchase_bill_id)
);

-- Add foreign key to purchase_bills after delivery_invoices is created
ALTER TABLE purchase_bills 
ADD CONSTRAINT fk_delivery_invoice 
FOREIGN KEY (delivery_invoice_id) 
REFERENCES delivery_invoices(id) 
ON DELETE SET NULL;

-- ============================================
-- AUDIT LOG (Track all changes)
-- ============================================
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    action VARCHAR(20) NOT NULL,  -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    user_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_purchase_bills_bill_number ON purchase_bills(bill_number);
CREATE INDEX idx_purchase_bills_farmer_id ON purchase_bills(farmer_id);
CREATE INDEX idx_purchase_bills_bill_date ON purchase_bills(bill_date);
CREATE INDEX idx_purchase_bills_is_delivered ON purchase_bills(is_delivered);
CREATE INDEX idx_purchase_bills_truck_id ON purchase_bills(truck_id);

CREATE INDEX idx_delivery_invoices_invoice_number ON delivery_invoices(invoice_number);
CREATE INDEX idx_delivery_invoices_mill_id ON delivery_invoices(mill_id);
CREATE INDEX idx_delivery_invoices_invoice_date ON delivery_invoices(invoice_date);

CREATE INDEX idx_delivery_items_delivery_id ON delivery_items(delivery_invoice_id);
CREATE INDEX idx_delivery_items_purchase_id ON delivery_items(purchase_bill_id);

CREATE INDEX idx_farmers_ic_number ON farmers(ic_number);
CREATE INDEX idx_farmers_name ON farmers(name);

CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- ============================================
-- VIEWS FOR REPORTING
-- ============================================

-- View: Purchase bills with full details
CREATE VIEW vw_purchase_bills_full AS
SELECT 
    pb.id,
    pb.bill_number,
    pb.bill_date,
    f.name AS farmer_name,
    f.ic_number AS farmer_ic,
    f.registration_number AS farmer_registration,
    t.truck_number,
    pb.weighbridge_receipt,
    pb.gross_weight,
    pb.discount_wap_basah,
    pb.discount_hampa_padi,
    pb.discount_padi_muda,
    pb.total_discount_percent,
    pb.discount_weight,
    pb.net_weight,
    pb.rice_price_per_1000kg,
    pb.total_payment,
    pb.subsidy_estimate,
    ha.area_name AS harvest_area,
    pb.is_delivered,
    di.invoice_number AS delivery_invoice_number,
    rm.mill_name AS delivery_mill_name
FROM purchase_bills pb
LEFT JOIN farmers f ON pb.farmer_id = f.id
LEFT JOIN trucks t ON pb.truck_id = t.id
LEFT JOIN harvest_areas ha ON pb.harvest_area_id = ha.id
LEFT JOIN delivery_invoices di ON pb.delivery_invoice_id = di.id
LEFT JOIN rice_mills rm ON di.mill_id = rm.id;

-- View: Delivery invoices with full details
CREATE VIEW vw_delivery_invoices_full AS
SELECT 
    di.id,
    di.invoice_number,
    di.invoice_date,
    rm.mill_name,
    rm.mill_code,
    t.truck_number,
    di.total_weight,
    COUNT(dit.purchase_bill_id) AS bill_count
FROM delivery_invoices di
LEFT JOIN rice_mills rm ON di.mill_id = rm.id
LEFT JOIN trucks t ON di.truck_id = t.id
LEFT JOIN delivery_items dit ON di.id = dit.delivery_invoice_id
GROUP BY di.id, di.invoice_number, di.invoice_date, 
         rm.mill_name, rm.mill_code, t.truck_number, di.total_weight;

-- ============================================
-- FUNCTIONS FOR AUTO-NUMBERING
-- ============================================

-- Function: Get next purchase bill number
CREATE OR REPLACE FUNCTION get_next_bill_number()
RETURNS VARCHAR(20) AS $$
DECLARE
    last_number INTEGER;
    next_number VARCHAR(20);
BEGIN
    SELECT CAST(bill_number AS INTEGER) INTO last_number
    FROM purchase_bills
    ORDER BY CAST(bill_number AS INTEGER) DESC
    LIMIT 1;
    
    IF last_number IS NULL THEN
        next_number := '13001';  -- Starting number
    ELSE
        next_number := CAST(last_number + 1 AS VARCHAR);
    END IF;
    
    RETURN next_number;
END;
$$ LANGUAGE plpgsql;

-- Function: Get next delivery invoice number
CREATE OR REPLACE FUNCTION get_next_invoice_number()
RETURNS VARCHAR(20) AS $$
DECLARE
    last_number INTEGER;
    next_number VARCHAR(20);
BEGIN
    SELECT CAST(invoice_number AS INTEGER) INTO last_number
    FROM delivery_invoices
    ORDER BY CAST(invoice_number AS INTEGER) DESC
    LIMIT 1;
    
    IF last_number IS NULL THEN
        next_number := '01001';  -- Starting number
    ELSE
        next_number := LPAD(CAST(last_number + 1 AS VARCHAR), 5, '0');
    END IF;
    
    RETURN next_number;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS FOR AUDIT LOGGING
-- ============================================

-- Function for audit logging
CREATE OR REPLACE FUNCTION audit_log_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, user_name)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', row_to_json(OLD), current_user);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_name)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW), current_user);
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, record_id, action, new_values, user_name)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', row_to_json(NEW), current_user);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers
CREATE TRIGGER audit_purchase_bills
AFTER INSERT OR UPDATE OR DELETE ON purchase_bills
FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

CREATE TRIGGER audit_delivery_invoices
AFTER INSERT OR UPDATE OR DELETE ON delivery_invoices
FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();

CREATE TRIGGER audit_farmers
AFTER INSERT OR UPDATE OR DELETE ON farmers
FOR EACH ROW EXECUTE FUNCTION audit_log_trigger();
```

---

## Application Architecture

### Project Structure

```
rice_billing_system/
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── setup.py                         # Installation script
├── README.md                        # Project documentation
├── .env                             # Environment variables (DB config)
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── database.py                  # Database connection configuration
│   ├── settings.py                  # Application settings
│   └── constants.py                 # Application constants
│
├── models/
│   ├── __init__.py
│   ├── base.py                      # SQLAlchemy base model
│   ├── config.py                    # Config model
│   ├── farmer.py                    # Farmer model
│   ├── rice_mill.py                 # Rice mill model
│   ├── truck.py                     # Truck model
│   ├── harvest_area.py              # Harvest area model
│   ├── purchase_bill.py             # Purchase bill model
│   ├── delivery_invoice.py          # Delivery invoice model
│   ├── delivery_item.py             # Delivery item model
│   └── audit_log.py                 # Audit log model
│
├── database/
│   ├── __init__.py
│   ├── connection.py                # Database connection manager
│   ├── session.py                   # Session management
│   └── migrations/                  # Alembic migrations
│       ├── versions/
│       ├── env.py
│       └── alembic.ini
│
├── services/
│   ├── __init__.py
│   ├── farmer_service.py            # Farmer CRUD operations
│   ├── rice_mill_service.py         # Rice mill CRUD operations
│   ├── truck_service.py             # Truck CRUD operations
│   ├── harvest_area_service.py      # Harvest area CRUD operations
│   ├── purchase_service.py          # Purchase bill operations
│   ├── delivery_service.py          # Delivery invoice operations
│   ├── calculation_service.py       # All calculation logic
│   ├── config_service.py            # Configuration management
│   └── audit_service.py             # Audit logging
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # Main application window
│   ├── styles.py                    # UI styling (QSS)
│   │
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── dashboard.py             # Dashboard screen
│   │   ├── purchase_entry.py        # Purchase bill entry screen
│   │   ├── delivery_entry.py        # Delivery invoice entry screen
│   │   ├── farmer_management.py     # Farmer management screen
│   │   ├── mill_management.py       # Rice mill management screen
│   │   ├── truck_management.py      # Truck management screen
│   │   ├── reports.py               # Reports screen
│   │   └── settings.py              # Settings screen
│   │
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── farmer_selector.py       # Farmer selection widget
│   │   ├── mill_selector.py         # Mill selection widget
│   │   ├── truck_selector.py        # Truck selection widget
│   │   ├── bill_table.py            # Purchase bills table widget
│   │   └── delivery_table.py        # Delivery invoices table widget
│   │
│   └── dialogs/
│       ├── __init__.py
│       ├── farmer_dialog.py         # Add/Edit farmer dialog
│       ├── mill_dialog.py           # Add/Edit mill dialog
│       ├── truck_dialog.py          # Add/Edit truck dialog
│       ├── search_dialog.py         # Search dialog
│       ├── settings_dialog.py       # Settings dialog
│       └── confirm_dialog.py        # Confirmation dialog
│
├── printing/
│   ├── __init__.py
│   ├── printer_manager.py           # Printer connection manager
│   ├── escpos_commands.py           # ESC/P command generator
│   ├── purchase_receipt.py          # Purchase bill receipt formatter
│   ├── delivery_receipt.py          # Delivery invoice receipt formatter
│   └── templates/
│       ├── purchase_template.txt    # Purchase receipt template
│       └── delivery_template.txt    # Delivery receipt template
│
├── utils/
│   ├── __init__.py
│   ├── validators.py                # Input validation functions
│   ├── formatters.py                # Number/date formatting
│   ├── helpers.py                   # Helper functions
│   └── exceptions.py                # Custom exceptions
│
├── api/                             # For future Flutter integration
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── farmers.py
│   │   ├── purchase_bills.py
│   │   └── delivery_invoices.py
│   └── schemas/
│       ├── __init__.py
│       ├── farmer_schema.py
│       ├── purchase_schema.py
│       └── delivery_schema.py
│
└── tests/
    ├── __init__.py
    ├── test_calculations.py         # Test calculation logic
    ├── test_services.py             # Test service layer
    ├── test_database.py             # Test database operations
    └── test_validators.py           # Test validation functions
```

---

## Core Business Logic

### Calculation Service (`services/calculation_service.py`)

```python
"""
Calculation Service
Contains all business calculation logic
"""

class CalculationService:
    
    @staticmethod
    def calculate_discount_weight(gross_weight: float, discount_percent: float) -> float:
        """
        Calculate discount weight based on gross weight and discount percentage
        
        Args:
            gross_weight: Gross weight in kg
            discount_percent: Discount percentage (0-100)
            
        Returns:
            Discount weight in kg
        """
        return round(gross_weight * (discount_percent / 100), 2)
    
    @staticmethod
    def calculate_net_weight(gross_weight: float, discount_weight: float) -> float:
        """
        Calculate net weight
        
        Args:
            gross_weight: Gross weight in kg
            discount_weight: Discount weight in kg
            
        Returns:
            Net weight in kg
        """
        return round(gross_weight - discount_weight, 2)
    
    @staticmethod
    def calculate_total_payment(net_weight: float, price_per_1000kg: float) -> float:
        """
        Calculate total payment based on net weight and price
        
        Args:
            net_weight: Net weight in kg
            price_per_1000kg: Price per 1000kg in RM
            
        Returns:
            Total payment in RM
        """
        return round((net_weight / 1000) * price_per_1000kg, 2)
    
    @staticmethod
    def calculate_subsidy_estimate(net_weight: float, subsidy_rate: float = 0.50) -> float:
        """
        Calculate subsidy estimate
        
        Args:
            net_weight: Net weight in kg
            subsidy_rate: Subsidy rate per kg (default 0.50)
            
        Returns:
            Subsidy estimate in RM
        """
        return round(net_weight * subsidy_rate, 2)
    
    @staticmethod
    def calculate_purchase_bill(
        gross_weight: float,
        discount_wap_basah: float,
        discount_hampa_padi: float,
        discount_padi_muda: float,
        rice_price: float,
        subsidy_rate: float = 0.50
    ) -> dict:
        """
        Complete purchase bill calculation
        
        Args:
            gross_weight: Gross weight in kg
            discount_wap_basah: Moisture discount %
            discount_hampa_padi: Empty grains discount %
            discount_padi_muda: Damaged rice discount %
            rice_price: Price per 1000kg
            subsidy_rate: Subsidy rate per kg
            
        Returns:
            Dictionary with all calculated values
        """
        # Calculate total discount percentage
        total_discount_percent = discount_wap_basah + discount_hampa_padi + discount_padi_muda
        
        # Calculate discount weight
        discount_weight = CalculationService.calculate_discount_weight(
            gross_weight, total_discount_percent
        )
        
        # Calculate net weight
        net_weight = CalculationService.calculate_net_weight(gross_weight, discount_weight)
        
        # Calculate total payment
        total_payment = CalculationService.calculate_total_payment(net_weight, rice_price)
        
        # Calculate subsidy estimate
        subsidy_estimate = CalculationService.calculate_subsidy_estimate(net_weight, subsidy_rate)
        
        return {
            'total_discount_percent': round(total_discount_percent, 2),
            'discount_weight': discount_weight,
            'net_weight': net_weight,
            'total_payment': total_payment,
            'subsidy_estimate': subsidy_estimate
        }
    
    @staticmethod
    def calculate_delivery_total_weight(purchase_bills: list) -> float:
        """
        Calculate total weight for delivery invoice
        
        Args:
            purchase_bills: List of purchase bill objects
            
        Returns:
            Total net weight in kg
        """
        return round(sum(bill.net_weight for bill in purchase_bills), 2)
```

### Example Usage:

```python
# Purchase bill calculation
result = CalculationService.calculate_purchase_bill(
    gross_weight=6680.00,
    discount_wap_basah=7.00,
    discount_hampa_padi=7.00,
    discount_padi_muda=6.00,
    rice_price=1500.00,
    subsidy_rate=0.50
)

# Result:
# {
#     'total_discount_percent': 20.00,
#     'discount_weight': 1336.00,
#     'net_weight': 5344.00,
#     'total_payment': 8016.00,
#     'subsidy_estimate': 2672.00
# }
```

---

## Data Validation Rules

### Input Validation (`utils/validators.py`)

```python
"""
Validation Rules
"""

import re
from datetime import datetime

class Validators:
    
    @staticmethod
    def validate_ic_number(ic: str) -> tuple[bool, str]:
        """
        Validate Malaysian IC number (12 digits)
        
        Returns:
            (is_valid, error_message)
        """
        if not ic:
            return False, "IC number is required"
        
        # Remove any spaces or dashes
        ic_clean = re.sub(r'[\s-]', '', ic)
        
        if not ic_clean.isdigit():
            return False, "IC number must contain only digits"
        
        if len(ic_clean) != 12:
            return False, "IC number must be 12 digits"
        
        return True, ""
    
    @staticmethod
    def validate_weight(weight: float, field_name: str = "Weight") -> tuple[bool, str]:
        """
        Validate weight value
        
        Returns:
            (is_valid, error_message)
        """
        if weight is None:
            return False, f"{field_name} is required"
        
        if weight <= 0:
            return False, f"{field_name} must be greater than 0"
        
        if weight > 1000000:  # 1 million kg max
            return False, f"{field_name} is too large"
        
        return True, ""
    
    @staticmethod
    def validate_percentage(percent: float, field_name: str = "Percentage") -> tuple[bool, str]:
        """
        Validate percentage value (0-100)
        
        Returns:
            (is_valid, error_message)
        """
        if percent is None:
            return False, f"{field_name} is required"
        
        if percent < 0 or percent > 100:
            return False, f"{field_name} must be between 0 and 100"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """
        Validate Malaysian phone number
        
        Returns:
            (is_valid, error_message)
        """
        if not phone:
            return True, ""  # Phone is optional
        
        # Remove spaces and dashes
        phone_clean = re.sub(r'[\s-]', '', phone)
        
        # Malaysian phone: 01X-XXXXXXX or 03-XXXXXXXX
        if not re.match(r'^0\d{8,10}$', phone_clean):
            return False, "Invalid phone number format"
        
        return True, ""
    
    @staticmethod
    def validate_truck_number(truck_number: str) -> tuple[bool, str]:
        """
        Validate truck number (alphanumeric with spaces/slashes)
        
        Returns:
            (is_valid, error_message)
        """
        if not truck_number:
            return False, "Truck number is required"
        
        if len(truck_number.strip()) < 2:
            return False, "Truck number is too short"
        
        if len(truck_number) > 20:
            return False, "Truck number is too long"
        
        return True, ""
    
    @staticmethod
    def validate_date(date: datetime) -> tuple[bool, str]:
        """
        Validate date (cannot be future)
        
        Returns:
            (is_valid, error_message)
        """
        if not date:
            return False, "Date is required"
        
        if date > datetime.now():
            return False, "Date cannot be in the future"
        
        return True, ""
    
    @staticmethod
    def validate_required_field(value, field_name: str) -> tuple[bool, str]:
        """
        Validate required field
        
        Returns:
            (is_valid, error_message)
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{field_name} is required"
        
        return True, ""
```

---

## Printing to Epson LQ-310

### Printer Manager (`printing/printer_manager.py`)

The Epson LQ-310 is a dot matrix printer that uses ESC/P (Epson Standard Code for Printers) commands.

**Key Points:**
- Character-based printing (not pixel-based)
- Fixed-width fonts (monospace)
- Line-by-line printing
- Paper width: Typically 80 columns for A4 paper
- USB connection

**ESC/P Commands:**
```python
ESC = chr(27)  # Escape character

# Common commands
INIT_PRINTER = ESC + '@'           # Initialize printer
BOLD_ON = ESC + 'E'                # Bold on
BOLD_OFF = ESC + 'F'               # Bold off
UNDERLINE_ON = ESC + '-' + chr(1)  # Underline on
UNDERLINE_OFF = ESC + '-' + chr(0) # Underline off
CENTER = ESC + 'a' + chr(1)        # Center alignment
LEFT = ESC + 'a' + chr(0)          # Left alignment
RIGHT = ESC + 'a' + chr(2)         # Right alignment
```

### Purchase Receipt Format (BIL BELIAN PADI)

```
================================================================================
                            AYOP BIN ARSHAD
       LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR
                        SELANGOR DARUL EHSAN

NO LESEN: 474523-K                              NO. TELEFON: 0162120051
================================================================================

                        BIL BELIAN : 13108

NAMA PETANI  : RUSIDAH BINTI ARDI               TARIKH: 25/11/2025 15:44
ALAMAT       : 0

NO DAFTAR PESAWAH: B002/11/25
NO KAD SUBSIDI   : 0
NO KAD PENGENALAN: 710502105256                 NO LORI: BDP/WES
NO AKAUN BANK    : 0                            NO RESIT TIMBANG: 017084

--------------------------------------------------------------------------------
Wap Basah: 7         Hampa Padi: 7        Padi Muda/Rosak: 6      = 20%
--------------------------------------------------------------------------------

BERAT TIMBANGAN (KG)         : 6,680.00
(-) POTONGAN                 : 1,336.00
BERAT BERSIH (KG)            : 5,344.00
HARGA (1000KG)               : RM 1,500.00
NILAI PADI                   : RM 8,016.00

Anggaran Subsidi             : 2,672.00

KAWASAN TUAIAN               : PASIR PANJANG
JUMLAH BAYARAN               : RM 8,016.00

================================================================================
DISEDIAKAN OLEH                              T. TANGAN PENERIMA




________________________________________________________________________________
SUBSIDI PADI
                            BIL BELIAN PADI
                         AYOP BIN ARSHAD
         LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR
================================================================================
```

### Delivery Receipt Format (INVOIS HANTARAN)

```
================================================================================
                         INVOIS HANTARAN                    No : 01876

                         AYOP BIN ARSHAD
         LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR
                        SELANGOR DARUL EHSAN.

No Lesen     : 474523-K                        Tarikh : 25/11/2025
No Telefon   : 0162120051

NO LORI      : WDP 7349
BERAT LORI   : 0

================================================================================

KEPADA:
            KILANG BERAS RAKYAT SEKINCHAN

                                              BERAT PADI    23,670.00

--------------------------------------------------------------------------------
NO BIL  NAMA PESAWAH                      BERAT PADI  NO LORI   NAMA KILANG
--------------------------------------------------------------------------------
13096   MOHD FUAD BIN ARSHAD                   9230   WDP 7349   KILANG BERAS
13097   SITI FITRIYATULAKMAL BINTI MD SHARI    4300   WDP 7349   KILANG BERAS
13098   ABDULLAH BIN IBAK                      7610   WDP 7349   KILANG BERAS
13099   SATAR BIN TALIP                        1200   WDP 7349   KILANG BERAS
13100   ISMAIL BIN ABUT                        1330   WDP 7349   KILANG BERAS
--------------------------------------------------------------------------------
                                    JUMLAH:   23,670 kg
================================================================================
```

---

## User Interface Mockup

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Rice Billing System - AYOP BIN ARSHAD                    [_] [□] [X]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [Dashboard] [Purchase] [Delivery] [Farmers] [Mills] [Reports] [Settings] │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DASHBOARD                                                              │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │   Today's        │  │   Pending        │  │   This Month     │    │
│  │   Purchases      │  │   Deliveries     │  │   Total          │    │
│  │                  │  │                  │  │                  │    │
│  │      15          │  │       8          │  │   RM 240,450.00  │    │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘    │
│                                                                          │
│  Recent Transactions                                                    │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ Bill No  │ Farmer Name        │ Net Weight │ Payment   │ Status│   │
│  ├──────────┼────────────────────┼────────────┼───────────┼───────┤   │
│  │ 13108    │ RUSIDAH BINTI ARDI │   5,344 kg │ RM 8,016  │ Paid  │   │
│  │ 13107    │ MOHD FUAD BIN...   │   9,230 kg │ RM 13,845 │ Paid  │   │
│  │ 13106    │ SITI FITRIYATUL... │   4,300 kg │ RM 6,450  │ Paid  │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Quick Actions                                                          │
│  [ New Purchase ]  [ Create Delivery ]  [ Search Bills ]                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Purchase Entry Screen

```
┌─────────────────────────────────────────────────────────────────────────┐
│ New Purchase Bill                                         [_] [□] [X]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Bill Information                                                       │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Bill Number: 13109 (Auto)      Date/Time: 25/11/2025 16:30   │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Farmer Information                                                     │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  IC Number: [_______________] [Search]  [Add New]              │   │
│  │                                                                  │   │
│  │  Name:             RUSIDAH BINTI ARDI                          │   │
│  │  Registration No:  B002/11/25                                   │   │
│  │  Address:          0                                            │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Weighing Information                                                   │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Truck Number:     [WDP 7349  ▼]  [Add New]                    │   │
│  │  Weighbridge No:   [_______________]                            │   │
│  │  Gross Weight:     [________] kg                                │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Discounts                                                              │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Wap Basah:        [7.00] %                                     │   │
│  │  Hampa Padi:       [7.00] %                                     │   │
│  │  Padi Muda/Rosak:  [6.00] %                                     │   │
│  │                                                                  │   │
│  │  Total Discount:   20.00 %                                      │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Calculations (Auto)                                                    │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Discount Weight:  1,336.00 kg                                  │   │
│  │  Net Weight:       5,344.00 kg                                  │   │
│  │  Price/1000kg:     RM 1,500.00                                  │   │
│  │  Total Payment:    RM 8,016.00                                  │   │
│  │  Subsidy Estimate: RM 2,672.00                                  │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Additional Information                                                 │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Harvest Area:     [PASIR PANJANG  ▼]                           │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  [ Save & Print ]  [ Save Only ]  [ Cancel ]                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Delivery Invoice Screen

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Create Delivery Invoice                                   [_] [□] [X]   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Delivery Information                                                   │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Invoice Number: 01877 (Auto)   Date: 25/11/2025              │   │
│  │  Rice Mill:      [KILANG BERAS RAKYAT SEKINCHAN ▼]            │   │
│  │  Truck:          [WDP 7349 ▼]                                  │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Available Purchase Bills (Not Yet Delivered)                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ [✓] │ Bill No │ Date     │ Farmer Name       │ Net Weight (kg)│   │
│  │─────┼─────────┼──────────┼───────────────────┼────────────────│   │
│  │ [✓] │ 13096   │25/11/2025│ MOHD FUAD BIN...  │      9,230     │   │
│  │ [✓] │ 13097   │25/11/2025│ SITI FITRIYATUL...│      4,300     │   │
│  │ [✓] │ 13098   │25/11/2025│ ABDULLAH BIN IBAK │      7,610     │   │
│  │ [✓] │ 13099   │25/11/2025│ SATAR BIN TALIP   │      1,200     │   │
│  │ [✓] │ 13100   │25/11/2025│ ISMAIL BIN ABUT   │      1,330     │   │
│  │ [ ] │ 13101   │25/11/2025│ ALI BIN AHMAD     │      5,800     │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  [ Select All ]  [ Deselect All ]  [ Filter by Mill ]                   │
│                                                                          │
│  Summary                                                                │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  Bills Selected:   5                                            │   │
│  │  Total Weight:     23,670.00 kg                                 │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  [ Create & Print ]  [ Cancel ]                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Required Python Packages

### requirements.txt

```txt
# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.13.0

# UI Framework
PyQt6==6.6.1
PyQt6-Qt6==6.6.1

# Printing
python-escpos==3.0
pywin32==306
pillow==10.1.0

# PDF Generation (for reports)
reportlab==4.0.7

# API (for future mobile integration)
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# Utilities
python-dotenv==1.0.0
python-dateutil==2.8.2

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# Logging
loguru==0.7.2
```

---

## Configuration

### .env File

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rice_billing_db
DB_USER=postgres
DB_PASSWORD=your_password_here

# Application Configuration
APP_NAME=Rice Billing System
APP_VERSION=1.0.0
DEBUG=True

# Printer Configuration
PRINTER_NAME=EPSON LQ-310
PRINTER_INTERFACE=usb

# Auto-numbering Start
START_BILL_NUMBER=13001
START_INVOICE_NUMBER=01001

# Business Configuration
DEFAULT_RICE_PRICE=1500.00
DEFAULT_SUBSIDY_RATE=0.50
DEFAULT_DISCOUNT_WAP_BASAH=7.00
DEFAULT_DISCOUNT_HAMPA_PADI=7.00
DEFAULT_DISCOUNT_PADI_MUDA=6.00

# Company Information
COMPANY_NAME=AYOP BIN ARSHAD
COMPANY_ADDRESS_1=LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR
COMPANY_ADDRESS_2=SELANGOR DARUL EHSAN
COMPANY_REGISTRATION=474523-K
COMPANY_PHONE=0162120051
COMPANY_MANAGER=AH SENG
```

---

## Development Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Set up project structure and database

- [ ] Create project structure
- [ ] Set up PostgreSQL database
- [ ] Create SQLAlchemy models
- [ ] Set up Alembic migrations
- [ ] Create database connection manager
- [ ] Implement configuration service
- [ ] Create basic UI framework (main window)
- [ ] Implement farmer management (CRUD)
- [ ] Implement rice mill management (CRUD)
- [ ] Implement truck management (CRUD)
- [ ] Implement harvest area management (CRUD)

### Phase 2: Purchase Bills (Week 3)
**Goal:** Complete purchase bill functionality

- [ ] Create calculation service
- [ ] Create purchase service (business logic)
- [ ] Build purchase entry screen
- [ ] Implement auto-numbering for bills
- [ ] Implement farmer selector widget
- [ ] Implement truck selector widget
- [ ] Implement real-time calculation updates
- [ ] Create purchase bill list/search screen
- [ ] Implement input validation
- [ ] Create purchase receipt template
- [ ] Implement printer manager
- [ ] Test printing to Epson LQ-310

### Phase 3: Delivery Invoices (Week 4)
**Goal:** Complete delivery invoice functionality

- [ ] Create delivery service (business logic)
- [ ] Build delivery invoice entry screen
- [ ] Implement bill selection/grouping by mill
- [ ] Implement auto-numbering for invoices
- [ ] Calculate delivery totals
- [ ] Create delivery receipt template
- [ ] Implement delivery invoice printing
- [ ] Update purchase bills as "delivered"
- [ ] Create delivery invoice list/search screen
- [ ] Test complete workflow (purchase → delivery)

### Phase 4: Reports & Enhancements (Week 5)
**Goal:** Add reporting and polish UI

- [ ] Create dashboard with statistics
- [ ] Implement date range reports
- [ ] Implement farmer transaction history
- [ ] Implement mill delivery history
- [ ] Export reports to PDF
- [ ] Export reports to Excel
- [ ] Create settings management screen
- [ ] Implement audit log viewer
- [ ] Add search functionality across all screens
- [ ] Polish UI/UX
- [ ] Add keyboard shortcuts
- [ ] Implement confirmation dialogs

### Phase 5: Testing & Deployment (Week 6)
**Goal:** Finalize and deploy

- [ ] Write unit tests for calculations
- [ ] Write unit tests for services
- [ ] Write integration tests
- [ ] Manual testing of all features
- [ ] Bug fixing
- [ ] Create user manual
- [ ] Create installation guide
- [ ] Build installer (PyInstaller/cx_Freeze)
- [ ] Create database backup script
- [ ] Create database restore script
- [ ] Deploy to production
- [ ] User training

---

## Future Enhancements (Post Phase 5)

### Phase 6: API Development (Optional)
- Build FastAPI REST API
- Create authentication system
- Implement API endpoints for all entities
- Add API documentation (Swagger)

### Phase 7: Mobile App (Optional)
- Build Flutter mobile app
- Implement mobile UI
- Connect to desktop API
- Test mobile-desktop synchronization

---

## Testing Scenarios

### Unit Tests

1. **Calculation Tests**
   ```python
   def test_calculate_discount_weight():
       result = CalculationService.calculate_discount_weight(6680.00, 20.00)
       assert result == 1336.00
   
   def test_calculate_net_weight():
       result = CalculationService.calculate_net_weight(6680.00, 1336.00)
       assert result == 5344.00
   
   def test_calculate_total_payment():
       result = CalculationService.calculate_total_payment(5344.00, 1500.00)
       assert result == 8016.00
   
   def test_calculate_subsidy_estimate():
       result = CalculationService.calculate_subsidy_estimate(5344.00, 0.50)
       assert result == 2672.00
   ```

2. **Validation Tests**
   ```python
   def test_validate_ic_number_valid():
       is_valid, msg = Validators.validate_ic_number("710502105256")
       assert is_valid == True
   
   def test_validate_ic_number_invalid():
       is_valid, msg = Validators.validate_ic_number("12345")
       assert is_valid == False
   
   def test_validate_weight_positive():
       is_valid, msg = Validators.validate_weight(6680.00)
       assert is_valid == True
   
   def test_validate_weight_negative():
       is_valid, msg = Validators.validate_weight(-100.00)
       assert is_valid == False
   ```

### Integration Tests

1. **Database Operations**
   - Create farmer → retrieve → update → delete
   - Create purchase bill → retrieve → link to delivery
   - Create delivery invoice → retrieve bills → calculate total

2. **Complete Workflow**
   - Add new farmer
   - Create purchase bill for farmer
   - Create another purchase bill for same mill
   - Create delivery invoice grouping both bills
   - Verify bills marked as delivered
   - Print both receipts
   - Search and view records

---

## Security Considerations

1. **Database Security**
   - Use environment variables for credentials
   - Never commit .env file to version control
   - Use parameterized queries (SQLAlchemy ORM handles this)
   - Regular database backups

2. **Data Integrity**
   - Foreign key constraints prevent orphaned records
   - Check constraints ensure valid data ranges
   - Audit log tracks all changes
   - Soft deletes for important records

3. **Input Validation**
   - Validate all user inputs
   - Sanitize inputs before database operations
   - Use appropriate data types
   - Implement max length limits

4. **Future Authentication**
   - Username/password system
   - Role-based access control
   - Session management
   - Audit trail with user tracking

---

## Backup and Recovery

### Automatic Backup Script

```python
"""
backup_database.py
Automatic PostgreSQL database backup
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

def backup_database():
    """Create PostgreSQL database backup"""
    # Configuration
    db_name = os.getenv('DB_NAME', 'rice_billing_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    
    # Backup directory
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_dir / f'rice_billing_backup_{timestamp}.sql'
    
    # pg_dump command
    command = [
        'pg_dump',
        '-h', db_host,
        '-p', db_port,
        '-U', db_user,
        '-F', 'c',  # Custom format
        '-b',  # Include large objects
        '-v',  # Verbose
        '-f', str(backup_file),
        db_name
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Backup created successfully: {backup_file}")
        
        # Keep only last 30 backups
        cleanup_old_backups(backup_dir, keep=30)
        
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e}")

def cleanup_old_backups(backup_dir, keep=30):
    """Remove old backup files, keeping only the most recent ones"""
    backups = sorted(backup_dir.glob('rice_billing_backup_*.sql'))
    if len(backups) > keep:
        for old_backup in backups[:-keep]:
            old_backup.unlink()
            print(f"Removed old backup: {old_backup}")

if __name__ == '__main__':
    backup_database()
```

### Restore Database

```bash
# Restore from backup
pg_restore -h localhost -p 5432 -U postgres -d rice_billing_db -v backup_file.sql
```

---

## Troubleshooting Guide

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL service is running
   - Verify credentials in .env file
   - Check firewall settings
   - Verify database exists

2. **Printer Not Found**
   - Check USB connection
   - Verify printer is powered on
   - Check printer is set as default
   - Verify printer driver installed

3. **Calculation Errors**
   - Check discount percentages sum to ≤100%
   - Verify gross weight > 0
   - Check price configuration

4. **Cannot Create Bill**
   - Verify farmer exists in database
   - Check truck exists in database
   - Validate all required fields filled
   - Check for duplicate bill numbers

---

## User Manual Outline

### 1. Getting Started
- System requirements
- Installation
- First-time setup
- Database configuration

### 2. Basic Operations
- Starting the application
- Navigating the interface
- Understanding the dashboard

### 3. Farmer Management
- Adding new farmers
- Editing farmer information
- Searching farmers
- Viewing farmer history

### 4. Creating Purchase Bills
- Entering farmer information
- Recording weights
- Setting discount percentages
- Reviewing calculations
- Saving and printing bills

### 5. Creating Delivery Invoices
- Selecting rice mill
- Selecting purchase bills
- Reviewing delivery summary
- Printing delivery invoice

### 6. Reports
- Viewing transaction history
- Generating date range reports
- Exporting to PDF/Excel
- Viewing audit logs

### 7. System Settings
- Updating rice price
- Changing discount defaults
- Managing company information
- Printer configuration

### 8. Troubleshooting
- Common issues and solutions
- Error messages explained
- Getting support

---

## Installation Package

### Building Executable with PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --name="Rice Billing System" \
            --windowed \
            --onefile \
            --icon=app_icon.ico \
            --add-data="printing/templates:templates" \
            --hidden-import=sqlalchemy.dialects.postgresql \
            main.py
```

### Installation Files Needed

```
installer/
├── setup.exe                    # Main installer
├── PostgreSQL_Installer.exe    # PostgreSQL bundled installer
├── config_template.env          # Template environment file
├── database_setup.sql           # Initial database setup script
├── README.txt                   # Installation instructions
└── User_Manual.pdf              # User manual
```

---

## Answers to Pre-Development Questions

Based on your requirements, here are recommended answers:

1. **Operating System:** Windows 10 and Windows 11 (64-bit)

2. **Multi-user:** Start with single computer, database on same machine. Can be expanded later to client-server architecture.

3. **Data Migration:** Plan for Excel import feature to migrate existing data.

4. **Receipt Paper:** Standard A4 paper (210mm width, 80 columns)

5. **Language:** Malay for receipts and UI (as shown in samples)

6. **Reprint Function:** Yes, allow reprinting. Track reprint count in audit log.

7. **Edit Function:** Allow editing before printing. After printing, only admin can edit with audit trail.

8. **Backup:** Automatic daily backups to configurable folder (default: ./backups/)

---

## Next Steps

1. **Review this specification** - Ensure all requirements are captured
2. **Set up development environment** - Install Python, PostgreSQL, IDE
3. **Create project structure** - Initialize Git repo, create folders
4. **Set up database** - Install PostgreSQL, create database, run schema
5. **Start Phase 1** - Begin with database models and basic CRUD operations

---

## Contact & Support

For questions during development:
- Review this specification document
- Check SQLAlchemy documentation: https://docs.sqlalchemy.org/
- Check PyQt6 documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Check python-escpos documentation: https://python-escpos.readthedocs.io/

---

**Document Version:** 1.0  
**Last Updated:** November 25, 2025  
**Author:** Development Team  
**Status:** Ready for Implementation
