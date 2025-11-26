# Receipt PDF Export - Implementation Guide

## Overview

The Receipt PDF Export feature allows users to export purchase bill and delivery invoice receipts to PDF format while maintaining the monospace, dot-matrix printer appearance. This provides a digital archiving solution that complements (or replaces) physical printer output.

## Features

### 1. Receipt PDF Service (`services/receipt_pdf_service.py`)

A new service that converts text-based receipts to PDF format with the following capabilities:

- **Monospace Font**: Uses Courier font to maintain the 80-column dot matrix appearance
- **Auto-generated Paths**: Automatically creates filenames and directories
- **Custom Output Paths**: Supports user-specified output locations
- **Bytes Output**: Can return PDF as bytes for in-memory operations
- **Multiple Receipt Types**: Handles both purchase bills and delivery invoices

#### Key Methods:

```python
# Export purchase bill receipt to PDF
ReceiptPdfService.export_purchase_receipt_pdf(
    db: Session,
    bill_id: int,
    output_path: Optional[str] = None,  # Auto-generated if None
    return_bytes: bool = False           # Return bytes instead of file
) -> Union[str, bytes]

# Export delivery invoice receipt to PDF
ReceiptPdfService.export_delivery_receipt_pdf(
    db: Session,
    invoice_id: int,
    output_path: Optional[str] = None,
    return_bytes: bool = False
) -> Union[str, bytes]

# Combined print and export
ReceiptPdfService.print_and_export(
    db: Session,
    bill_or_invoice_id: int,
    receipt_type: str,              # 'purchase' or 'delivery'
    do_print: bool = True,
    do_export: bool = True,
    output_path: Optional[str] = None
) -> Optional[str]
```

### 2. Receipt Export Dialog (`ui/dialogs/receipt_export_dialog.py`)

A user-friendly dialog that presents three options when printing receipts:

1. **Print to Printer** - Print to console (printer integration pending)
2. **Save as PDF** - Export receipt to PDF file
3. **Both** - Print and save PDF simultaneously (default option)

**Features:**
- Radio button selection for output method
- Optional custom PDF output path with file browser
- Auto-generated filename suggestion
- Clear, informative UI with descriptions

### 3. Updated Screens

#### Purchase List Screen (`ui/screens/purchase_list.py`)
- Modified `print_receipt()` method to show the export dialog
- Handles all three output options
- Shows success messages with PDF location
- Offers to open PDF file after creation

#### Delivery List Screen (`ui/screens/delivery_list.py`)
- Same enhancements as purchase list
- Consistent user experience across both receipt types

## User Workflow

### From Purchase Bills Screen:

1. User selects a purchase bill from the list
2. Clicks "Print Receipt" button
3. Dialog appears with three options:
   - Print to Printer (Console)
   - Save as PDF
   - Both (Print & Save PDF) ← **DEFAULT**
4. User can optionally specify custom PDF path via "Browse..." button
5. User clicks "OK"
6. System processes the request:
   - If Print: Receipt printed to console with clear markers
   - If PDF: Receipt exported to PDF (auto-generated or custom path)
   - If Both: Both actions performed
7. Success message shows PDF location
8. User asked if they want to open the PDF file
9. If yes, PDF opens in system default viewer

### From Delivery Invoices Screen:

Same workflow as purchase bills, but for delivery invoices.

## Technical Details

### PDF Generation

**Font Configuration:**
```python
FONT_NAME = 'Courier'      # Built-in monospace font
FONT_SIZE = 9              # Smaller to fit 80 columns
LINE_HEIGHT = 12           # Points between lines
CHARS_PER_LINE = 80        # Receipt template width
```

**Page Settings:**
```python
PAGE_SIZE = A4
MARGIN_LEFT = 20mm
MARGIN_TOP = 20mm
MARGIN_BOTTOM = 20mm
```

**Auto-pagination:**
- Automatically creates new pages when content exceeds page height
- Maintains consistent formatting across pages

### Directory Structure

**Default Export Directory:**
```
./exports/receipts/
```

**Can be customized via environment variable:**
```bash
export RECEIPT_PDF_DIR=/path/to/custom/directory
```

**Auto-generated Filenames:**
```
receipt_purchase_{bill_number}_{timestamp}.pdf
receipt_delivery_{invoice_number}_{timestamp}.pdf
```

Example:
```
receipt_purchase_13001_20251126_143052.pdf
receipt_delivery_01001_20251126_143112.pdf
```

### Receipt Templates

The PDF export uses the existing text-based receipt templates:

**Purchase Template:**
```
printing/templates/purchase_template.txt
```

**Delivery Template:**
```
printing/templates/delivery_template.txt
```

These templates are formatted with:
- 80 character width
- Malay language labels
- Border separators (=, -, _)
- Aligned fields
- Company header and footer

## Error Handling

The implementation includes comprehensive error handling:

```python
class ReceiptPdfError(Exception):
    """Base exception for receipt PDF errors"""
    pass
```

**Common Errors:**
- Bill/Invoice not found
- File system permission issues
- Invalid output paths
- PDF generation failures

All errors are caught and displayed to the user with clear messages.

## Testing

### Test Script: `test_receipt_pdf_export.py`

Run the test script to verify functionality:

```bash
python test_receipt_pdf_export.py
```

**Tests include:**
1. Export to auto-generated path
2. Export to custom path
3. Export as bytes (in-memory)
4. Both purchase bills and delivery invoices
5. Text receipt preview comparison

**Expected Output:**
```
===============================================================================
PURCHASE RECEIPT PDF EXPORT: ALL TESTS PASSED
===============================================================================

===============================================================================
DELIVERY RECEIPT PDF EXPORT: ALL TESTS PASSED
===============================================================================

TEST SUMMARY
Purchase Receipt PDF                     PASSED
Delivery Receipt PDF                     PASSED
===============================================================================

ALL TESTS PASSED!
```

## Integration Points

### 1. Existing Receipt Formatters

The PDF service uses the existing receipt formatters:
- `printing.purchase_receipt.PurchaseReceiptFormatter`
- `printing.delivery_receipt.DeliveryReceiptFormatter`

This ensures consistency between console output, PDF output, and future printer output.

### 2. Service Layer

Integrates with existing services:
- `services.purchase_service.PurchaseService`
- `services.delivery_service.DeliveryService`
- `services.config_service.ConfigService`

### 3. Database Layer

Queries the database directly for bill/invoice data:
- Uses SQLAlchemy ORM models
- Includes relationship loading for efficient queries

## Platform Compatibility

### PDF Opening (Cross-platform)

```python
if platform.system() == 'Windows':
    os.startfile(file_path)
elif platform.system() == 'Darwin':  # macOS
    subprocess.run(['open', file_path])
else:  # Linux
    subprocess.run(['xdg-open', file_path])
```

Automatically uses the system's default PDF viewer.

## Future Enhancements

### Potential Additions:

1. **Batch PDF Export**
   - Export multiple receipts in a single PDF
   - Already supported by existing `PdfExportService`

2. **Email Integration**
   - Email PDF receipts to farmers
   - Use `return_bytes=True` to attach to email

3. **Physical Printer Integration**
   - Replace console output with actual Epson LQ-310 printing
   - Use the same receipt text generation

4. **Print Preview**
   - Show PDF preview before exporting
   - Use `return_bytes=True` to display in dialog

5. **Watermarks**
   - Add "COPY" or "DUPLICATE" watermarks for reprints
   - Timestamp reprints

6. **Digital Signatures**
   - Add digital signature to PDFs
   - Verify receipt authenticity

## Configuration

### Environment Variables:

```bash
# Custom PDF export directory
RECEIPT_PDF_DIR=/path/to/receipts

# Company information (from ConfigService)
COMPANY_NAME="AYOP BIN ARSHAD"
COMPANY_ADDRESS_1="LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR"
COMPANY_ADDRESS_2="SELANGOR DARUL EHSAN"
COMPANY_REGISTRATION="474523-K"
COMPANY_PHONE="0162120051"
```

## Usage Examples

### Example 1: Simple Export

```python
from services.receipt_pdf_service import ReceiptPdfService
from config.database import get_db

db = get_db()

# Export purchase bill to PDF
pdf_path = ReceiptPdfService.export_purchase_receipt_pdf(
    db=db,
    bill_id=1
)

print(f"PDF exported to: {pdf_path}")
```

### Example 2: Custom Path

```python
# Export to specific location
pdf_path = ReceiptPdfService.export_purchase_receipt_pdf(
    db=db,
    bill_id=1,
    output_path="/path/to/custom/receipt.pdf"
)
```

### Example 3: In-Memory PDF

```python
# Get PDF as bytes for email or other use
pdf_bytes = ReceiptPdfService.export_purchase_receipt_pdf(
    db=db,
    bill_id=1,
    return_bytes=True
)

# Send via email, upload to cloud, etc.
send_email_with_attachment(pdf_bytes)
```

### Example 4: Print and Export

```python
# Print to console AND save PDF
pdf_path = ReceiptPdfService.print_and_export(
    db=db,
    bill_or_invoice_id=1,
    receipt_type='purchase',
    do_print=True,
    do_export=True
)
```

## Troubleshooting

### Issue: PDF not opening automatically

**Solution:** Check system default PDF viewer settings

### Issue: Permission denied when saving

**Solution:**
- Check directory permissions
- Ensure `exports/receipts/` directory is writable
- Try custom output path in user's home directory

### Issue: Font not rendering correctly

**Solution:**
- Courier is a built-in PDF font, should always work
- If issues persist, check ReportLab installation:
  ```bash
  pip install --upgrade reportlab
  ```

### Issue: Receipt text truncated

**Solution:**
- Check LINE_HEIGHT and FONT_SIZE settings
- Adjust for longer receipts
- Pagination should handle long receipts automatically

## File Locations

### New Files Created:

```
services/receipt_pdf_service.py          # Main PDF service
ui/dialogs/receipt_export_dialog.py      # Export dialog
test_receipt_pdf_export.py               # Test script
RECEIPT_PDF_EXPORT_GUIDE.md              # This guide
```

### Modified Files:

```
ui/screens/purchase_list.py              # Updated print_receipt()
ui/screens/delivery_list.py              # Updated print_receipt()
```

### Generated Files (at runtime):

```
exports/receipts/                        # PDF output directory
  receipt_purchase_*.pdf                 # Purchase bill PDFs
  receipt_delivery_*.pdf                 # Delivery invoice PDFs
```

## Summary

The Receipt PDF Export feature provides a complete solution for converting text-based receipts to professional PDF documents. It maintains the monospace formatting of the original dot matrix printer output while providing modern digital archiving capabilities.

**Key Benefits:**
- No dependency on physical printer for archiving
- Easy email distribution of receipts
- Searchable PDF documents
- Consistent formatting across all receipt types
- User-friendly dialog interface
- Cross-platform compatibility
- Extensible for future enhancements
