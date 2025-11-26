# PDF Export Service - Complete Documentation

## Overview

The PDF Export Service provides professional PDF generation capabilities for the Rice Billing System. It supports exporting purchase bills, delivery invoices, batch exports, and date range reports with full formatting in Malay language.

## Features

- **Single Document Export**: Export individual purchase bills or delivery invoices
- **Batch Export**: Combine multiple purchase bills into one PDF
- **Date Range Reports**: Generate summary reports for specific time periods
- **Dual Output Modes**: Save to file or return as bytes for API/email
- **Professional Formatting**: Clean, well-structured PDFs with company branding
- **Malay Language Support**: All labels and headers in Bahasa Malaysia
- **Currency & Weight Formatting**: Proper RM and kg formatting with thousand separators
- **Error Handling**: Comprehensive exception handling with custom error types

## Architecture

### File Structure

```
services/
  pdf_export_service.py          # Main PDF export service

examples/
  pdf_export_examples.py         # Integration examples

tests/
  test_pdf_export.py             # Unit tests

models/
  purchase_bill.py               # Updated with relationships
  delivery_invoice.py            # Updated with relationships
```

### Dependencies

The service requires ReportLab (already in requirements.txt):

```python
reportlab==4.0.7
```

## Service API

### Class: PdfExportService

#### Methods

##### 1. export_purchase_bill()

Export a single purchase bill to PDF.

**Signature:**
```python
@staticmethod
def export_purchase_bill(
    db: Session,
    bill_id: int,
    output_path: Optional[str] = None,
    return_bytes: bool = False
) -> Union[str, bytes]
```

**Parameters:**
- `db` (Session): SQLAlchemy database session
- `bill_id` (int): Purchase bill ID to export
- `output_path` (str, optional): Custom output file path. If None, auto-generated
- `return_bytes` (bool): If True, return PDF as bytes instead of saving to file

**Returns:**
- `str`: File path if `return_bytes=False`
- `bytes`: PDF content if `return_bytes=True`

**Raises:**
- `PurchaseBillNotFoundError`: If bill with given ID doesn't exist
- `PdfExportError`: If PDF generation fails

**Example:**
```python
from services.pdf_export_service import PdfExportService

# Export to auto-generated file
file_path = PdfExportService.export_purchase_bill(db, bill_id=1)
print(f"PDF saved to: {file_path}")

# Export to bytes for API response
pdf_bytes = PdfExportService.export_purchase_bill(db, bill_id=1, return_bytes=True)
```

---

##### 2. export_delivery_invoice()

Export a single delivery invoice to PDF.

**Signature:**
```python
@staticmethod
def export_delivery_invoice(
    db: Session,
    invoice_id: int,
    output_path: Optional[str] = None,
    return_bytes: bool = False
) -> Union[str, bytes]
```

**Parameters:**
- `db` (Session): SQLAlchemy database session
- `invoice_id` (int): Delivery invoice ID to export
- `output_path` (str, optional): Custom output file path
- `return_bytes` (bool): If True, return PDF as bytes

**Returns:**
- `str` or `bytes`: File path or PDF bytes

**Raises:**
- `DeliveryInvoiceNotFoundError`: If invoice not found
- `PdfExportError`: If PDF generation fails

**Example:**
```python
# Export delivery invoice
file_path = PdfExportService.export_delivery_invoice(db, invoice_id=1)
```

---

##### 3. export_multiple_bills_batch()

Export multiple purchase bills in a single PDF document.

**Signature:**
```python
@staticmethod
def export_multiple_bills_batch(
    db: Session,
    bill_ids: List[int],
    output_path: Optional[str] = None,
    return_bytes: bool = False
) -> Union[str, bytes]
```

**Parameters:**
- `db` (Session): Database session
- `bill_ids` (List[int]): List of purchase bill IDs to include
- `output_path` (str, optional): Custom output path
- `return_bytes` (bool): Return bytes if True

**Returns:**
- `str` or `bytes`: File path or PDF bytes

**Raises:**
- `PdfExportError`: If bill_ids is empty or generation fails

**Example:**
```python
# Export multiple bills
bill_ids = [1, 2, 3, 4, 5]
file_path = PdfExportService.export_multiple_bills_batch(db, bill_ids)
```

---

##### 4. export_date_range_report()

Generate a date range report for purchase bills or delivery invoices.

**Signature:**
```python
@staticmethod
def export_date_range_report(
    db: Session,
    start_date: date,
    end_date: date,
    report_type: str = 'purchase',
    output_path: Optional[str] = None,
    return_bytes: bool = False
) -> Union[str, bytes]
```

**Parameters:**
- `db` (Session): Database session
- `start_date` (date): Start date of range (inclusive)
- `end_date` (date): End date of range (inclusive)
- `report_type` (str): Either 'purchase' or 'delivery'
- `output_path` (str, optional): Custom output path
- `return_bytes` (bool): Return bytes if True

**Returns:**
- `str` or `bytes`: File path or PDF bytes

**Raises:**
- `InvalidDateRangeError`: If start_date > end_date
- `PdfExportError`: If generation fails

**Example:**
```python
from datetime import date, timedelta

# Last 30 days purchase report
end_date = date.today()
start_date = end_date - timedelta(days=30)

file_path = PdfExportService.export_date_range_report(
    db,
    start_date,
    end_date,
    report_type='purchase'
)
```

---

### Exception Classes

#### PdfExportError
Base exception for all PDF export errors.

#### PurchaseBillNotFoundError
Raised when a purchase bill with the specified ID is not found.

#### DeliveryInvoiceNotFoundError
Raised when a delivery invoice with the specified ID is not found.

#### InvalidDateRangeError
Raised when the date range is invalid (start > end).

**Usage:**
```python
from services.pdf_export_service import (
    PdfExportService,
    PurchaseBillNotFoundError,
    PdfExportError
)

try:
    pdf = PdfExportService.export_purchase_bill(db, bill_id=999)
except PurchaseBillNotFoundError as e:
    print(f"Bill not found: {e}")
except PdfExportError as e:
    print(f"Export failed: {e}")
```

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# PDF Export Configuration
PDF_EXPORT_DIR=./exports/pdf        # Directory for exported PDFs
PDF_AUTO_OPEN=false                 # Auto-open PDF after generation (future)
```

### Company Information

The service uses company information from environment variables (or database config):

```bash
COMPANY_NAME=AYOP BIN ARSHAD
COMPANY_ADDRESS_1=LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR
COMPANY_ADDRESS_2=SELANGOR DARUL EHSAN
COMPANY_REGISTRATION=474523-K
COMPANY_PHONE=0162120051
```

---

## PDF Content Details

### Purchase Bill PDF Includes:

1. **Company Header**
   - Company name, address, registration, phone

2. **Bill Information**
   - Bill number
   - Date

3. **Farmer Information**
   - Name, IC number
   - Address, phone
   - Registration number
   - Subsidy code
   - Bank account

4. **Weighing Information**
   - Truck number
   - Weighbridge receipt
   - Harvest area

5. **Discount Breakdown**
   - Wap Basah (Moisture) %
   - Hampa Padi (Empty grains) %
   - Padi Muda/Rosak (Damaged) %
   - Total discount %

6. **Calculations**
   - Gross weight
   - Discount weight
   - Net weight
   - Price per 1000kg
   - Total payment
   - Subsidy estimate

### Delivery Invoice PDF Includes:

1. **Company Header**
   - Standard company information

2. **Invoice Details**
   - Invoice number
   - Date

3. **Delivery Information**
   - Rice mill name and address
   - Truck number and tare weight

4. **Purchase Bills Table**
   - List of all bills in delivery
   - Bill numbers
   - Farmer names
   - Individual weights
   - Dates

5. **Summary**
   - Total weight delivered

### Batch Export PDF Includes:

- Multiple purchase bills in simplified format
- Page breaks between bills
- Summary table for each bill

### Date Range Report PDF Includes:

**Purchase Report:**
- Summary statistics (total bills, weight, payment)
- Detailed table of all bills in range
- Sorted by date

**Delivery Report:**
- Summary statistics (total invoices, weight)
- Detailed table of all invoices
- Mill and truck information

---

## Integration Patterns

### 1. Desktop Application (PyQt6)

```python
from PyQt6.QtWidgets import QPushButton, QMessageBox, QFileDialog
from services.pdf_export_service import PdfExportService

class PurchaseBillScreen:
    def setup_export_button(self):
        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(self.on_export_pdf)

    def on_export_pdf(self):
        """Handle PDF export button click"""
        if not self.current_bill_id:
            QMessageBox.warning(self, "Warning", "No bill selected")
            return

        try:
            # Ask where to save
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF",
                f"bill_{self.current_bill_id}.pdf",
                "PDF Files (*.pdf)"
            )

            if file_path:
                # Export
                result = PdfExportService.export_purchase_bill(
                    self.db,
                    self.current_bill_id,
                    output_path=file_path
                )

                QMessageBox.information(
                    self,
                    "Success",
                    f"PDF exported to:\n{result}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
```

### 2. REST API (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from services.pdf_export_service import PdfExportService

app = FastAPI()

@app.get("/api/bills/{bill_id}/pdf")
def download_bill_pdf(bill_id: int):
    """Download purchase bill as PDF"""
    try:
        pdf_bytes = PdfExportService.export_purchase_bill(
            db=get_db(),
            bill_id=bill_id,
            return_bytes=True
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=bill_{bill_id}.pdf"
            }
        )
    except PurchaseBillNotFoundError:
        raise HTTPException(status_code=404, detail="Bill not found")
```

### 3. Email Attachment

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

def email_purchase_bill(bill_id: int, recipient_email: str):
    """Send purchase bill PDF via email"""

    # Generate PDF as bytes
    pdf_bytes = PdfExportService.export_purchase_bill(
        db=get_db(),
        bill_id=bill_id,
        return_bytes=True
    )

    # Create email
    msg = MIMEMultipart()
    msg['From'] = "billing@example.com"
    msg['To'] = recipient_email
    msg['Subject'] = f"Purchase Bill #{bill_id}"

    # Email body
    body = "Please find attached your purchase bill."
    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
    pdf_attachment.add_header(
        'Content-Disposition',
        'attachment',
        filename=f'purchase_bill_{bill_id}.pdf'
    )
    msg.attach(pdf_attachment)

    # Send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("your_email@gmail.com", "password")
        server.send_message(msg)
```

### 4. Scheduled Reports

```python
import schedule
import time
from datetime import date, timedelta

def generate_daily_reports():
    """Generate daily reports automatically"""
    yesterday = date.today() - timedelta(days=1)

    # Purchase report
    PdfExportService.export_date_range_report(
        db=get_db(),
        start_date=yesterday,
        end_date=yesterday,
        report_type='purchase'
    )

    # Delivery report
    PdfExportService.export_date_range_report(
        db=get_db(),
        start_date=yesterday,
        end_date=yesterday,
        report_type='delivery'
    )

# Schedule to run daily at 6 AM
schedule.every().day.at("06:00").do(generate_daily_reports)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Testing

### Running Unit Tests

```bash
# Run all PDF export tests
pytest tests/test_pdf_export.py -v

# Run specific test
pytest tests/test_pdf_export.py::TestPdfExportService::test_export_purchase_bill_to_bytes -v

# Run with coverage
pytest tests/test_pdf_export.py --cov=services.pdf_export_service --cov-report=html
```

### Test Coverage

The test suite includes:
- Formatting functions (currency, weight, date)
- Export directory creation
- Purchase bill export (file & bytes)
- Delivery invoice export (file & bytes)
- Batch export
- Date range reports (purchase & delivery)
- Error handling (not found, invalid ranges)
- Edge cases

---

## Performance Considerations

### Memory Usage

- **File Mode**: Low memory usage, streams directly to disk
- **Bytes Mode**: Entire PDF in memory, suitable for small-medium PDFs
- **Batch Export**: Memory scales with number of bills

### Recommendations

- For API responses: Use `return_bytes=True` (convenient)
- For large batch exports: Use `return_bytes=False` (memory efficient)
- For scheduled jobs: Always save to file for audit trail

### Optimization Tips

1. **Use eager loading**: The service uses `joinedload()` to reduce queries
2. **Batch exports**: Combine multiple bills to reduce overhead
3. **Index database**: Ensure indexes on `bill_date`, `invoice_date` for reports
4. **Cache company info**: Company info is fetched once per PDF

---

## Customization

### Adding Custom Fields to PDF

To add new fields to purchase bill PDF:

1. Update the data table in `export_purchase_bill()`:

```python
farmer_data = [
    ["MAKLUMAT PETANI", ""],
    ["Nama:", farmer.name],
    # Add your new field here
    ["New Field:", bill.new_field_value],
]
```

2. Adjust table styling if needed

### Changing PDF Layout

The service uses ReportLab's Platypus for layout. Key components:

- **Page Size**: A4 (default), configurable via `PAGE_WIDTH`, `PAGE_HEIGHT`
- **Margins**: 15mm, configurable via `MARGIN`
- **Styles**: Defined in `_create_styles()`
- **Colors**: Use `colors.HexColor('#rrggbb')`

### Custom Report Types

To add a new report type:

```python
@staticmethod
def export_farmer_summary_report(db: Session, farmer_id: int):
    """Custom report for farmer's purchase history"""

    # Fetch data
    bills = db.query(PurchaseBill).filter(
        PurchaseBill.farmer_id == farmer_id
    ).all()

    # Build PDF (similar to existing methods)
    # ...
```

---

## Troubleshooting

### Common Issues

**Issue: "Module 'reportlab' not found"**
```bash
# Solution: Install reportlab
pip install reportlab==4.0.7
```

**Issue: "Permission denied" when saving PDF**
```bash
# Solution: Check export directory permissions
chmod 755 ./exports/pdf
```

**Issue: PDF contains garbled text**
```bash
# Solution: Ensure UTF-8 encoding for Malay characters
# The service handles this automatically
```

**Issue: "PurchaseBillNotFoundError"**
```python
# Solution: Verify bill exists before export
bill = db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()
if not bill:
    print("Bill does not exist")
```

**Issue: Large batch export consumes too much memory**
```python
# Solution: Use file mode instead of bytes mode
PdfExportService.export_multiple_bills_batch(
    db, bill_ids,
    return_bytes=False  # Save to file
)
```

---

## Best Practices

1. **Always close database sessions** after PDF generation
2. **Use try-except blocks** to handle errors gracefully
3. **Validate inputs** before calling export methods
4. **Use return_bytes=True** only when necessary (API, email)
5. **Keep export directory organized** with timestamped filenames
6. **Log export operations** for audit trail
7. **Test with actual data** to ensure proper formatting
8. **Handle missing data gracefully** (N/A for optional fields)
9. **Use transactions** when updating records after export
10. **Backup export directory** regularly

---

## Future Enhancements

Potential improvements for future versions:

1. **PDF Watermarks**: Add "DRAFT" or "COPY" watermarks
2. **Digital Signatures**: Sign PDFs with company certificate
3. **Email Integration**: Built-in email sending
4. **Cloud Storage**: Direct upload to S3/Google Drive
5. **Template System**: User-customizable PDF templates
6. **Multi-language**: Support English alongside Malay
7. **QR Codes**: Add QR code for verification
8. **Charts/Graphs**: Visual analytics in reports
9. **Print Queue**: Manage pending PDF print jobs
10. **Batch Operations**: Async generation for large exports

---

## Support

For issues or questions:

1. Check this documentation
2. Review examples in `examples/pdf_export_examples.py`
3. Run unit tests to verify installation
4. Check logs for detailed error messages
5. Consult ReportLab documentation for layout customization

---

## Change Log

### Version 1.0.0 (2025-11-26)
- Initial release
- Purchase bill PDF export
- Delivery invoice PDF export
- Batch export functionality
- Date range reports
- Comprehensive error handling
- Unit tests
- Integration examples
