# Receipt PDF Export - Quick Start Guide

## What's New?

You can now export receipts to PDF instead of just printing to the console!

## How to Use

### From the Application:

1. **Select a purchase bill or delivery invoice** from the list
2. **Click "Print Receipt"** button
3. **Choose your option** in the dialog:
   - **Print to Printer** - Print to console (for now)
   - **Save as PDF** - Export to PDF file
   - **Both** - Print and save PDF (recommended)
4. **Optionally choose custom location** using "Browse..." button
5. **Click OK**
6. **Open the PDF** when prompted (or find it later in `exports/receipts/`)

### Default Behavior:

- **Default Option:** Both (Print & Save PDF)
- **Default Location:** `./exports/receipts/`
- **Filename Format:** `receipt_purchase_13001_20251126_143052.pdf`

## Testing

Run the test script to verify everything works:

```bash
python test_receipt_pdf_export.py
```

Expected output: All tests should PASS

## Programmatic Usage

### Quick Export:

```python
from services.receipt_pdf_service import ReceiptPdfService
from config.database import get_db

db = get_db()

# Export purchase bill
pdf_path = ReceiptPdfService.export_purchase_receipt_pdf(
    db=db,
    bill_id=1
)

print(f"Saved to: {pdf_path}")
```

### Custom Path:

```python
pdf_path = ReceiptPdfService.export_purchase_receipt_pdf(
    db=db,
    bill_id=1,
    output_path="/my/custom/path/receipt.pdf"
)
```

### Get PDF Bytes:

```python
pdf_bytes = ReceiptPdfService.export_purchase_receipt_pdf(
    db=db,
    bill_id=1,
    return_bytes=True
)
# Use bytes for email, upload, etc.
```

### Delivery Invoices:

```python
pdf_path = ReceiptPdfService.export_delivery_receipt_pdf(
    db=db,
    invoice_id=1
)
```

## Features

- Monospace font (like dot matrix printer)
- 80-column format maintained
- Auto-pagination for long receipts
- Cross-platform PDF opening
- Malay language support
- Same format as console output

## File Locations

**Service:** `/home/appfelix/claude/program_beli_padi/services/receipt_pdf_service.py`

**Dialog:** `/home/appfelix/claude/program_beli_padi/ui/dialogs/receipt_export_dialog.py`

**Updated Screens:**
- `/home/appfelix/claude/program_beli_padi/ui/screens/purchase_list.py`
- `/home/appfelix/claude/program_beli_padi/ui/screens/delivery_list.py`

**Output Directory:** `./exports/receipts/`

## Configuration

Set custom export directory:

```bash
export RECEIPT_PDF_DIR=/path/to/custom/directory
```

Or set in `.env` file:

```
RECEIPT_PDF_DIR=/path/to/custom/directory
```

## Troubleshooting

**Q: Where are my PDFs saved?**
A: Check `./exports/receipts/` or the custom path you specified

**Q: Can I change the default directory?**
A: Yes, set `RECEIPT_PDF_DIR` environment variable

**Q: PDF won't open automatically?**
A: Check your system's default PDF viewer settings. You can still open the file manually from the location shown in the success message.

**Q: Can I export multiple receipts at once?**
A: Not yet through the UI, but you can use the existing `PdfExportService.export_multiple_bills_batch()` method programmatically.

## Next Steps

For detailed information, see:
- **Full Guide:** `RECEIPT_PDF_EXPORT_GUIDE.md`
- **Test Script:** `test_receipt_pdf_export.py`
- **API Documentation:** See docstrings in `services/receipt_pdf_service.py`

## Example Output

When you export a receipt, you'll see:

```
Receipt printed to console and exported to PDF!

PDF Location: ./exports/receipts/receipt_purchase_13001_20251126_143052.pdf

Note: Physical printer integration not yet implemented.

Would you like to open the PDF file now?
[Yes] [No]
```

The PDF will look exactly like the console output but in a professional PDF format with monospace font.
