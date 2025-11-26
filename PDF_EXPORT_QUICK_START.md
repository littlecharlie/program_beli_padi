# PDF Export Service - Quick Start Guide

## Installation

The PDF export service is already integrated. ReportLab is included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Basic Usage

### 1. Export a Purchase Bill

```python
from services.pdf_export_service import PdfExportService
from database.session import get_db

db = get_db()

# Export to auto-generated file
file_path = PdfExportService.export_purchase_bill(
    db=db,
    bill_id=1
)
print(f"PDF saved: {file_path}")
# Output: PDF saved: ./exports/pdf/purchase_bill_13001_20251126_143022.pdf
```

### 2. Export a Delivery Invoice

```python
# Export delivery invoice
file_path = PdfExportService.export_delivery_invoice(
    db=db,
    invoice_id=1
)
print(f"Invoice PDF: {file_path}")
```

### 3. Batch Export Multiple Bills

```python
# Export 5 bills in one PDF
bill_ids = [1, 2, 3, 4, 5]
file_path = PdfExportService.export_multiple_bills_batch(
    db=db,
    bill_ids=bill_ids
)
print(f"Batch PDF: {file_path}")
```

### 4. Generate Monthly Report

```python
from datetime import date

# Current month's purchase report
start_date = date(2025, 11, 1)
end_date = date(2025, 11, 30)

file_path = PdfExportService.export_date_range_report(
    db=db,
    start_date=start_date,
    end_date=end_date,
    report_type='purchase'
)
print(f"Report saved: {file_path}")
```

### 5. Get PDF as Bytes (for API)

```python
# For API response or email attachment
pdf_bytes = PdfExportService.export_purchase_bill(
    db=db,
    bill_id=1,
    return_bytes=True
)

# Use in FastAPI
from fastapi.responses import Response

return Response(
    content=pdf_bytes,
    media_type="application/pdf"
)
```

## Error Handling

```python
from services.pdf_export_service import (
    PdfExportService,
    PurchaseBillNotFoundError,
    PdfExportError
)

try:
    pdf = PdfExportService.export_purchase_bill(db, bill_id=999)
except PurchaseBillNotFoundError:
    print("Bill not found!")
except PdfExportError as e:
    print(f"Export failed: {e}")
```

## Configuration

Edit `.env` to customize:

```bash
# Where to save PDFs
PDF_EXPORT_DIR=./exports/pdf

# Company info (appears in PDFs)
COMPANY_NAME=AYOP BIN ARSHAD
COMPANY_ADDRESS_1=LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR
COMPANY_ADDRESS_2=SELANGOR DARUL EHSAN
COMPANY_REGISTRATION=474523-K
COMPANY_PHONE=0162120051
```

## PyQt6 Integration Example

```python
from PyQt6.QtWidgets import QPushButton, QMessageBox

class YourScreen:
    def setup_ui(self):
        # Add export button
        self.btn_export = QPushButton("Export PDF")
        self.btn_export.clicked.connect(self.on_export_clicked)

    def on_export_clicked(self):
        try:
            file_path = PdfExportService.export_purchase_bill(
                self.db,
                self.current_bill_id
            )
            QMessageBox.information(
                self, "Success",
                f"PDF exported:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Export failed:\n{str(e)}"
            )
```

## Testing

Run tests to verify installation:

```bash
# Run all tests
pytest tests/test_pdf_export.py -v

# Quick smoke test
pytest tests/test_pdf_export.py::TestPdfExportService::test_format_currency -v
```

## What's Next?

- See `PDF_EXPORT_DOCUMENTATION.md` for complete API reference
- Check `examples/pdf_export_examples.py` for more integration patterns
- Customize PDF layout in `services/pdf_export_service.py`

## Common Use Cases

### Use Case 1: Print Button in UI
```python
def on_print_button_clicked(self):
    # Generate PDF
    pdf_path = PdfExportService.export_purchase_bill(self.db, self.bill_id)

    # Open with default PDF viewer (optional)
    import os
    os.startfile(pdf_path)  # Windows
    # subprocess.call(['open', pdf_path])  # macOS
    # subprocess.call(['xdg-open', pdf_path])  # Linux
```

### Use Case 2: Email to Farmer
```python
def email_bill_to_farmer(bill_id: int, email: str):
    # Generate PDF as bytes
    pdf_bytes = PdfExportService.export_purchase_bill(
        db, bill_id, return_bytes=True
    )

    # Attach to email
    send_email(
        to=email,
        subject="Your Purchase Bill",
        attachment=pdf_bytes,
        filename=f"bill_{bill_id}.pdf"
    )
```

### Use Case 3: End-of-Day Report
```python
from datetime import date

def generate_daily_report():
    today = date.today()

    # Purchase bills report
    purchase_pdf = PdfExportService.export_date_range_report(
        db, today, today, report_type='purchase'
    )

    # Delivery invoices report
    delivery_pdf = PdfExportService.export_date_range_report(
        db, today, today, report_type='delivery'
    )

    print(f"Daily reports generated:\n{purchase_pdf}\n{delivery_pdf}")
```

## Troubleshooting

**Problem**: PDF not generating
- Check if database session is valid
- Verify bill/invoice ID exists
- Check PDF_EXPORT_DIR has write permissions

**Problem**: Missing data in PDF
- Verify relationships are loaded (service handles this)
- Check if optional fields (truck, harvest area) are null

**Problem**: "Module not found" error
- Run: `pip install reportlab==4.0.7`
- Restart your application

## Performance Tips

1. **For single exports**: Use default settings
2. **For batch exports**: Export to file (`return_bytes=False`)
3. **For API responses**: Use bytes mode (`return_bytes=True`)
4. **For large reports**: Consider pagination or date filtering

## Support

- Full documentation: `PDF_EXPORT_DOCUMENTATION.md`
- Examples: `examples/pdf_export_examples.py`
- Tests: `tests/test_pdf_export.py`
- GitHub: https://github.com/littlecharlie/program_beli_padi

---

That's it! You're ready to export PDFs. Start with a simple purchase bill export and expand from there.
