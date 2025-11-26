# PDF Export Implementation Guide

## Overview

This guide explains the comprehensive PDF export UI components added to the Rice Billing System. The implementation provides professional PDF export functionality for both Purchase Bills and Delivery Invoices with multiple user interaction patterns.

## Architecture

### Component Structure

```
ui/
├── dialogs/
│   └── pdf_export_dialog.py          # Export dialogs (full & quick)
├── widgets/
│   ├── export_helpers.py              # Helper utilities & notifications
│   └── context_menu_mixin.py          # Reusable context menu functionality
└── screens/
    ├── purchase_list_with_export.py   # Enhanced purchase list screen
    └── delivery_list_with_export.py   # Enhanced delivery list screen
```

## Key Components

### 1. PDF Export Dialogs

#### `PdfExportDialog` (Full Dialog)
Comprehensive export dialog with all options:
- **File Location**: Browse, quick shortcuts (Desktop, Documents, Downloads)
- **Export Options**: Page format (A4/Letter/Legal), quality settings
- **Include Options**: Headers, footers, page numbers
- **Batch Options**: One per page, summary page
- **Post-Export**: Auto-open file/folder

```python
from ui.dialogs.pdf_export_dialog import PdfExportDialog

dialog = PdfExportDialog(
    export_type="purchase",  # or "delivery"
    item_count=5,
    default_filename="purchase_bills_20250126.pdf",
    parent=self
)

if dialog.exec():
    config = dialog.get_export_config()
    # config contains all export settings
```

#### `QuickPdfExportDialog` (Simplified)
Quick export for single items with minimal options:
- **File Selection**: Browse with auto-suggested location
- **Auto-Open**: Checkbox to open after export

```python
from ui.dialogs.pdf_export_dialog import QuickPdfExportDialog

dialog = QuickPdfExportDialog(
    export_type="purchase",
    default_filename="bill_13001_20250126.pdf",
    parent=self
)

if dialog.exec():
    config = dialog.get_export_config()
```

#### `BatchExportProgressDialog`
Progress tracking for batch exports:
- Progress bar with item count
- Current item indicator
- Cancellable operation

```python
from ui.dialogs.pdf_export_dialog import BatchExportProgressDialog

progress = BatchExportProgressDialog(total_items=10, parent=self)
progress.show()

for idx, item in enumerate(items, 1):
    progress.update_progress(idx, item.bill_number)
    # Generate PDF for item

progress.set_completed()
```

### 2. Export Helper Utilities

#### `ExportNotification`
Standardized notification system:

```python
from ui.widgets.export_helpers import ExportNotification

# Success notification
ExportNotification.show_success(self, file_path, item_count=1)

# Error notification
ExportNotification.show_error(self, "Failed to generate PDF")

# Warning
ExportNotification.show_warning(self, "Some items were skipped")

# Confirm overwrite
if ExportNotification.confirm_overwrite(self, file_path):
    # Proceed with overwrite
```

#### `FileOperations`
File system operations:

```python
from ui.widgets.export_helpers import FileOperations

# Open PDF with default viewer
FileOperations.open_file("/path/to/file.pdf")

# Open folder containing file
FileOperations.open_folder("/path/to/file.pdf")

# Ensure PDF extension
path = FileOperations.ensure_pdf_extension("file")  # Returns "file.pdf"

# Get unique filename if exists
unique = FileOperations.get_unique_filename("/path/to/file.pdf")
# Returns "/path/to/file_1.pdf" if original exists

# Validate path
is_valid, error = FileOperations.validate_path("/path/to/file.pdf")
```

#### Helper Functions

```python
from ui.widgets.export_helpers import generate_export_filename, format_file_size

# Generate standardized filename
filename = generate_export_filename(
    export_type="purchase",
    identifier="13001",
    timestamp=True
)
# Returns "purchase_bill_13001_20250126_153045.pdf"

# Format file size
size = format_file_size(1048576)  # Returns "1.0 MB"
```

### 3. Context Menu Mixin

#### `TableContextMenuMixin`
Adds right-click context menu to table widgets:

```python
from ui.widgets.context_menu_mixin import TableContextMenuMixin

class MyScreen(QWidget, TableContextMenuMixin):
    def __init__(self):
        super().__init__()
        self.bills_table = QTableWidget()

        # Setup context menu
        self.setup_table_context_menu(self.bills_table, export_enabled=True)

        # Connect signals
        self.export_single_pdf.connect(self._export_single)
        self.export_batch_pdf.connect(self._export_batch)
        self.view_details.connect(self._view_details)
        self.edit_item.connect(self._edit_item)
        self.delete_item.connect(self._delete_item)
        self.print_receipt.connect(self._print_receipt)
```

**Context Menu Features:**
- View Details (single selection)
- Edit (single selection)
- Export as PDF (single or batch)
- Print Receipt (single selection)
- Delete (single or batch)
- Keyboard shortcuts (Ctrl+P, Ctrl+E, Delete)

## User Workflows

### Workflow 1: Export Single Bill/Invoice

1. **From List Screen**:
   - User clicks on a bill/invoice row
   - Right-clicks → "Export as PDF"
   - OR clicks toolbar "Export Selected" button

2. **Dialog Opens**:
   - Quick export dialog appears
   - Default location: Documents folder
   - Filename auto-generated: `purchase_bill_13001_20250126_153045.pdf`
   - "Open PDF after export" checked by default

3. **User Actions**:
   - Optionally browse to different location
   - Click "Export"

4. **Post-Export**:
   - Success notification appears
   - PDF opens automatically (if checked)
   - Folder opens (if checked)

### Workflow 2: Export Multiple Bills/Invoices

1. **From List Screen**:
   - User selects multiple rows (Ctrl+Click or Shift+Click)
   - Right-clicks → "Export N items as PDF"
   - OR clicks "Export Selected" button

2. **Dialog Opens**:
   - Full export dialog with all options
   - Batch-specific options visible:
     - ✓ One item per page
     - ✓ Include summary page
   - Quality selection (Standard/High)

3. **Export Process**:
   - Progress dialog shows
   - Updates for each item
   - Can cancel mid-operation

4. **Completion**:
   - Success notification with item count
   - Post-export actions execute

### Workflow 3: Export All/Filtered Results

1. **From List Screen**:
   - User applies filters (date range, status, mill)
   - Clicks "Export All to PDF" button

2. **Confirmation** (if large dataset):
   - "Export N items to PDF?"
   - Shows estimated file size

3. **Export Proceeds**:
   - Full dialog appears
   - Batch export with progress
   - All current results exported

### Workflow 4: Quick Export from Detail View

1. **From Detail Dialog**:
   - User viewing bill/invoice details
   - Clicks "Export" button in dialog

2. **Quick Export**:
   - Minimal dialog
   - One-click export
   - Opens automatically

## Integration Guide

### Adding Export to Existing Screen

#### Step 1: Import Required Components

```python
from ui.dialogs.pdf_export_dialog import PdfExportDialog, QuickPdfExportDialog
from ui.widgets.export_helpers import (
    ExportNotification, FileOperations, generate_export_filename
)
from ui.widgets.context_menu_mixin import TableContextMenuMixin
```

#### Step 2: Add Mixin to Class

```python
class MyScreen(QWidget, TableContextMenuMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... existing code ...
```

#### Step 3: Setup Context Menu

```python
def setup_ui(self):
    # ... create table ...

    # Setup context menu
    self.setup_table_context_menu(self.my_table, export_enabled=True)

    # Connect signals
    self.export_single_pdf.connect(self._export_single)
    self.export_batch_pdf.connect(self._export_batch)
```

#### Step 4: Add Export Buttons

```python
def _create_toolbar(self):
    layout = QHBoxLayout()

    export_btn = QPushButton("Export Selected to PDF")
    export_btn.setProperty("success", True)
    export_btn.clicked.connect(self._export_selected)
    layout.addWidget(export_btn)

    return layout
```

#### Step 5: Implement Export Methods

```python
def _export_single(self, item_id: int):
    """Export single item to PDF"""
    item = self.service.get_by_id(self.db, item_id)
    if not item:
        return

    filename = generate_export_filename("purchase", item.bill_number)
    dialog = QuickPdfExportDialog("purchase", filename, self)

    if dialog.exec():
        config = dialog.get_export_config()
        self._perform_export(item, config)

def _export_batch(self, item_ids: list):
    """Export multiple items to PDF"""
    filename = generate_export_filename("purchase", f"{len(item_ids)}_bills")
    dialog = PdfExportDialog("purchase", len(item_ids), filename, self)

    if dialog.exec():
        config = dialog.get_export_config()
        self._perform_batch_export(item_ids, config)

def _perform_export(self, item, config: dict):
    """Actually generate the PDF"""
    try:
        file_path = config['file_path']

        # TODO: Implement PDF generation
        # success = PdfGenerator.generate(item, file_path, config)

        ExportNotification.show_success(self, file_path, 1)

        if config.get('open_file'):
            FileOperations.open_file(file_path)

    except Exception as e:
        ExportNotification.show_error(self, str(e))
```

### Replacing Existing Screens

To use the enhanced screens with export functionality:

#### In `main_window.py`:

```python
# Old import
# from ui.screens.purchase_list import PurchaseListScreen

# New import
from ui.screens.purchase_list_with_export import PurchaseListScreenWithExport

# In __init__:
# self.purchase_list_screen = PurchaseListScreen(self)
self.purchase_list_screen = PurchaseListScreenWithExport(self)
```

## Styling

The PDF export components follow the existing dark mode theme:

### Dialog Styling
- Background: `#1e1e1e` (Deep Charcoal)
- Surfaces: `#2d2d2d` (Card background)
- Primary: `#4da6ff` (Blue)
- Success: `#4caf50` (Green)
- Text: `#e0e0e0` (High contrast)

### Context Menu Styling
- Dark background with hover effects
- Primary blue for selected items
- Clear visual hierarchy

### Button Variants
```python
# Primary Export Button
export_btn.setProperty("success", True)  # Green

# Secondary Button
browse_btn.setProperty("secondary", True)  # Gray

# Danger Button (if needed)
delete_btn.setProperty("danger", True)  # Red
```

## TODO: Actual PDF Generation

The UI components are complete, but **PDF generation is not yet implemented**.

### Next Steps:

1. **Install PDF Library**:
   ```bash
   pip install reportlab PyPDF2
   ```

2. **Create PDF Generator Module**:
   ```
   printing/
   └── pdf_generator.py
   ```

3. **Implement PDF Generation**:
   ```python
   class PdfGenerator:
       @staticmethod
       def generate_purchase_bill(bill, file_path, config):
           """Generate PDF for purchase bill"""
           # Use ReportLab to create PDF
           # Match existing receipt format
           # Apply config options (headers, footers, etc.)

       @staticmethod
       def generate_delivery_invoice(invoice, file_path, config):
           """Generate PDF for delivery invoice"""
           # Similar to purchase bill
           # Include all associated bills

       @staticmethod
       def generate_batch_pdf(items, file_path, config):
           """Generate batch PDF"""
           # If one_per_page: separate pages
           # If include_summary: add summary page
   ```

4. **Replace Placeholders**:
   In `purchase_list_with_export.py`:
   ```python
   # Replace
   success = self._generate_purchase_bill_pdf(bill, file_path, config)

   # With
   from printing.pdf_generator import PdfGenerator
   success = PdfGenerator.generate_purchase_bill(bill, file_path, config)
   ```

### PDF Layout Recommendations

**Purchase Bill PDF**:
- Header: Company name, address, registration
- Bill Info: Bill number, date, farmer details
- Weights: Gross, discounts, net weight
- Calculations: Price breakdown, total payment, subsidy
- Footer: Page number, export date

**Delivery Invoice PDF**:
- Header: Company info
- Invoice Info: Invoice number, date, mill, truck
- Bills Table: All included bills with details
- Summary: Total bills, total weight, total payment
- Footer: Page numbers

**Batch PDF**:
- Cover page: Summary statistics
- Individual pages: Each bill/invoice
- Final page: Grand totals

## Testing Checklist

- [ ] Single bill export dialog opens correctly
- [ ] Batch export dialog shows correct item count
- [ ] Quick export auto-fills Documents folder
- [ ] Browse button opens file dialog
- [ ] Quick location shortcuts work (Desktop, Documents, Downloads)
- [ ] Context menu appears on right-click
- [ ] Export options persist between dialogs
- [ ] Progress dialog updates correctly
- [ ] Progress dialog can be cancelled
- [ ] Success notification shows with correct path
- [ ] Error notification shows on failure
- [ ] Open file action works (cross-platform)
- [ ] Open folder action works (cross-platform)
- [ ] Keyboard shortcuts work (Ctrl+P for export)
- [ ] Multi-selection works correctly
- [ ] Filtered export only exports visible items
- [ ] File overwrite confirmation appears
- [ ] Unique filename generation works
- [ ] Path validation prevents invalid locations

## Platform Considerations

### Windows
- File paths use backslashes
- `os.startfile()` for opening files
- Explorer for folder selection

### macOS
- File paths use forward slashes
- `open` command for files/folders
- Finder integration

### Linux
- File paths use forward slashes
- `xdg-open` for files/folders
- File manager integration

## Configuration

### Default Settings

Can be configured in settings screen:

```python
DEFAULT_EXPORT_LOCATION = "Documents"  # Desktop, Documents, Downloads
DEFAULT_PAGE_FORMAT = "A4"             # A4, Letter, Legal
DEFAULT_QUALITY = "standard"           # standard, high
DEFAULT_AUTO_OPEN = True               # Open PDF after export
DEFAULT_ONE_PER_PAGE = True            # Batch: one item per page
DEFAULT_INCLUDE_SUMMARY = True         # Batch: include summary
```

### User Preferences

Store in database `config` table:
- `pdf_default_location`
- `pdf_page_format`
- `pdf_quality`
- `pdf_auto_open`
- `pdf_one_per_page`
- `pdf_include_summary`

## File Naming Convention

Format: `{type}_{identifier}_{timestamp}.pdf`

Examples:
- `purchase_bill_13001_20250126_153045.pdf`
- `purchase_bills_5_items_20250126_153045.pdf`
- `delivery_invoice_01001_20250126_153045.pdf`
- `delivery_invoices_3_items_20250126_153045.pdf`

## Performance Considerations

- **Large Batch Exports**: Show warning for >50 items
- **Progress Updates**: Update every 5% to avoid UI lag
- **Memory Management**: Stream to file, don't build entire PDF in memory
- **Cancellation**: Check cancellation flag every iteration
- **Error Handling**: Continue on single item failure, show summary at end

## Accessibility

- Keyboard navigation supported
- Screen reader friendly labels
- High contrast mode compatible
- Tooltips for all buttons
- Clear error messages

## Future Enhancements

1. **Email Export**: Direct email attachment
2. **Cloud Upload**: Upload to Google Drive, Dropbox
3. **Template Selection**: Multiple PDF templates
4. **Watermarks**: Add watermarks to drafts
5. **Digital Signatures**: Sign PDFs electronically
6. **Batch Actions**: Schedule recurring exports
7. **Export History**: Track exported files
8. **Preview**: PDF preview before export

## Support

For issues or questions:
1. Check error logs in console
2. Verify file permissions
3. Test with simple export first
4. Check PDF library installation
5. Verify cross-platform file paths
