# PDF Export Service

Professional PDF generation for Rice Billing System purchase bills, delivery invoices, and reports.

## Quick Install

```bash
# Install dependencies (ReportLab already in requirements.txt)
pip install -r requirements.txt

# Verify installation
python test_pdf_export_installation.py
```

## Quick Start

```python
from services.pdf_export_service import PdfExportService
from database.session import get_db

db = get_db()

# Export a purchase bill
file_path = PdfExportService.export_purchase_bill(db, bill_id=1)
print(f"PDF saved: {file_path}")
```

## Features

- ✅ Single purchase bill PDF export
- ✅ Single delivery invoice PDF export
- ✅ Batch export (multiple bills in one PDF)
- ✅ Date range reports (purchase & delivery)
- ✅ File or bytes output modes
- ✅ Professional formatting with company branding
- ✅ Malay language support
- ✅ Currency & weight formatting (RM, kg)
- ✅ Comprehensive error handling

## Main Methods

### 1. Export Purchase Bill

```python
# To file (auto-generated name)
file_path = PdfExportService.export_purchase_bill(db, bill_id=1)

# To custom path
file_path = PdfExportService.export_purchase_bill(
    db, bill_id=1,
    output_path="/path/to/bill.pdf"
)

# To bytes (for API/email)
pdf_bytes = PdfExportService.export_purchase_bill(
    db, bill_id=1,
    return_bytes=True
)
```

### 2. Export Delivery Invoice

```python
file_path = PdfExportService.export_delivery_invoice(db, invoice_id=1)
```

### 3. Batch Export

```python
bill_ids = [1, 2, 3, 4, 5]
file_path = PdfExportService.export_multiple_bills_batch(db, bill_ids)
```

### 4. Date Range Report

```python
from datetime import date, timedelta

end_date = date.today()
start_date = end_date - timedelta(days=30)

# Purchase report
file_path = PdfExportService.export_date_range_report(
    db, start_date, end_date, report_type='purchase'
)

# Delivery report
file_path = PdfExportService.export_date_range_report(
    db, start_date, end_date, report_type='delivery'
)
```

## Configuration

Add to `.env`:

```bash
PDF_EXPORT_DIR=./exports/pdf
PDF_AUTO_OPEN=false
```

Company info (already in .env):

```bash
COMPANY_NAME=AYOP BIN ARSHAD
COMPANY_ADDRESS_1=LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR
COMPANY_ADDRESS_2=SELANGOR DARUL EHSAN
COMPANY_REGISTRATION=474523-K
COMPANY_PHONE=0162120051
```

## PyQt6 Integration

```python
from PyQt6.QtWidgets import QPushButton, QMessageBox

class YourScreen:
    def setup_ui(self):
        self.btn_export = QPushButton("Export PDF")
        self.btn_export.clicked.connect(self.on_export)

    def on_export(self):
        try:
            path = PdfExportService.export_purchase_bill(
                self.db, self.bill_id
            )
            QMessageBox.information(self, "Success", f"Saved: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
```

## Error Handling

```python
from services.pdf_export_service import (
    PdfExportService,
    PurchaseBillNotFoundError,
    DeliveryInvoiceNotFoundError,
    InvalidDateRangeError,
    PdfExportError
)

try:
    pdf = PdfExportService.export_purchase_bill(db, bill_id=999)
except PurchaseBillNotFoundError:
    print("Bill not found")
except PdfExportError as e:
    print(f"Export failed: {e}")
```

## Testing

```bash
# Run installation test
python test_pdf_export_installation.py

# Run unit tests
pytest tests/test_pdf_export.py -v

# Run with coverage
pytest tests/test_pdf_export.py --cov=services.pdf_export_service
```

## Documentation

- **Quick Start**: [PDF_EXPORT_QUICK_START.md](PDF_EXPORT_QUICK_START.md)
- **Full API Docs**: [PDF_EXPORT_DOCUMENTATION.md](PDF_EXPORT_DOCUMENTATION.md)
- **Implementation**: [PDF_EXPORT_IMPLEMENTATION_SUMMARY.md](PDF_EXPORT_IMPLEMENTATION_SUMMARY.md)
- **Examples**: [examples/pdf_export_examples.py](examples/pdf_export_examples.py)

## File Locations

```
services/
  pdf_export_service.py          # Main service (1100+ lines)

tests/
  test_pdf_export.py             # Unit tests (380+ lines)

examples/
  pdf_export_examples.py         # Integration examples (450+ lines)

models/
  purchase_bill.py               # Updated with relationships
  delivery_invoice.py            # Updated with relationships

.env                             # Updated with PDF config
```

## What's Included in PDFs

### Purchase Bill PDF
- Company header (name, address, license, phone)
- Bill number and date
- Farmer information (IC, name, address, bank account, etc.)
- Weighing details (truck, weighbridge receipt, harvest area)
- Discount breakdown (Wap Basah, Hampa Padi, Padi Muda/Rosak)
- Calculations (gross, discount, net weight, price, payment, subsidy)

### Delivery Invoice PDF
- Company header
- Invoice number and date
- Mill information (name, address, phone)
- Truck details (number, tare weight)
- List of all purchase bills in delivery
- Total weight summary

### Reports
- Summary statistics
- Detailed tables
- Date range filtering
- Proper formatting and totals

## Common Use Cases

### 1. Print Bill After Creation
```python
def save_purchase_bill(self):
    # Save bill to database
    bill = create_bill(...)
    db.commit()

    # Generate PDF
    pdf_path = PdfExportService.export_purchase_bill(db, bill.id)

    # Optional: Auto-open
    import os
    os.startfile(pdf_path)  # Windows
```

### 2. Email to Farmer
```python
def email_bill_to_farmer(bill_id, email):
    pdf_bytes = PdfExportService.export_purchase_bill(
        db, bill_id, return_bytes=True
    )
    send_email(to=email, attachment=pdf_bytes)
```

### 3. Daily Report
```python
def generate_daily_report():
    today = date.today()
    PdfExportService.export_date_range_report(
        db, today, today, report_type='purchase'
    )
```

### 4. API Endpoint
```python
@app.get("/bills/{bill_id}/pdf")
def download_pdf(bill_id: int):
    pdf = PdfExportService.export_purchase_bill(
        db, bill_id, return_bytes=True
    )
    return Response(content=pdf, media_type="application/pdf")
```

## Troubleshooting

**Q: "Module 'reportlab' not found"**
```bash
A: pip install reportlab==4.0.7
```

**Q: "Permission denied" error**
```bash
A: Check PDF_EXPORT_DIR permissions
   mkdir -p ./exports/pdf
   chmod 755 ./exports/pdf
```

**Q: "Bill not found" error**
```python
A: Verify bill exists before exporting
   bill = db.query(PurchaseBill).filter_by(id=bill_id).first()
   if not bill:
       print("Bill doesn't exist")
```

**Q: Missing data in PDF**
```python
A: Optional fields show "N/A" when null
   This is expected behavior for truck, harvest area, etc.
```

## Performance

- Single export: ~100-200ms
- Batch export: Linear scaling
- Memory: Low in file mode, moderate in bytes mode
- Database: Optimized with eager loading

## Next Steps

1. ✅ Verify installation: `python test_pdf_export_installation.py`
2. ✅ Run tests: `pytest tests/test_pdf_export.py -v`
3. ✅ Read Quick Start: `PDF_EXPORT_QUICK_START.md`
4. ✅ Try examples: `examples/pdf_export_examples.py`
5. ✅ Integrate with UI: Add export buttons to screens

## Support

- Examples: See `examples/pdf_export_examples.py`
- Tests: See `tests/test_pdf_export.py`
- Full docs: See `PDF_EXPORT_DOCUMENTATION.md`
- ReportLab: https://www.reportlab.com/docs/

---

**Ready to use!** The PDF export service is fully implemented, tested, and documented.

Start with:
```python
from services.pdf_export_service import PdfExportService
file_path = PdfExportService.export_purchase_bill(db, bill_id=1)
print(f"Success: {file_path}")
```
