# PDF Export - Quick Reference Card

## Import Statements

```python
# Dialogs
from ui.dialogs.pdf_export_dialog import (
    PdfExportDialog,           # Full-featured export dialog
    QuickPdfExportDialog,      # Simplified quick export
    BatchExportProgressDialog  # Progress tracking
)

# Helpers
from ui.widgets.export_helpers import (
    ExportNotification,        # Notifications
    FileOperations,            # File operations
    generate_export_filename,  # Filename generator
    format_file_size           # Size formatter
)

# Context Menu
from ui.widgets.context_menu_mixin import (
    TableContextMenuMixin      # Right-click menu
)
```

## Common Patterns

### Pattern 1: Add Context Menu to Table

```python
class MyScreen(QWidget, TableContextMenuMixin):
    def __init__(self):
        super().__init__()
        self.table = QTableWidget()

        # Setup context menu
        self.setup_table_context_menu(self.table, export_enabled=True)

        # Connect signals
        self.export_single_pdf.connect(self._handle_single)
        self.export_batch_pdf.connect(self._handle_batch)
```

### Pattern 2: Single Item Export

```python
def _handle_single(self, item_id: int):
    item = Service.get_by_id(self.db, item_id)
    filename = generate_export_filename("type", item.number)

    dialog = QuickPdfExportDialog("type", filename, self)
    if dialog.exec():
        config = dialog.get_export_config()
        self._export_to_pdf(item, config)
```

### Pattern 3: Batch Export

```python
def _handle_batch(self, item_ids: list):
    filename = generate_export_filename("type", f"{len(item_ids)}_items")

    dialog = PdfExportDialog("type", len(item_ids), filename, self)
    if dialog.exec():
        config = dialog.get_export_config()
        self._batch_export(item_ids, config)
```

### Pattern 4: Show Notifications

```python
# Success
ExportNotification.show_success(self, file_path, item_count)

# Error
ExportNotification.show_error(self, "Error message")

# Warning
ExportNotification.show_warning(self, "Warning message")

# Confirm overwrite
if ExportNotification.confirm_overwrite(self, file_path):
    # Proceed
```

### Pattern 5: File Operations

```python
# Open PDF
FileOperations.open_file(file_path)

# Open folder
FileOperations.open_folder(file_path)

# Validate path
valid, error = FileOperations.validate_path(file_path)
if not valid:
    print(error)

# Ensure extension
path = FileOperations.ensure_pdf_extension("file")  # "file.pdf"

# Get unique name
unique = FileOperations.get_unique_filename(path)
```

## Quick Integration Checklist

- [ ] Import `TableContextMenuMixin`
- [ ] Add mixin to class: `class MyScreen(QWidget, TableContextMenuMixin)`
- [ ] Call `setup_table_context_menu(table)` in `setup_ui()`
- [ ] Connect signals: `export_single_pdf`, `export_batch_pdf`
- [ ] Implement handlers: `_handle_single()`, `_handle_batch()`
- [ ] Add export buttons to UI (optional)
- [ ] Test right-click menu appears
- [ ] Test single item export
- [ ] Test batch export

## Dialog Options Reference

### QuickPdfExportDialog

```python
dialog = QuickPdfExportDialog(
    export_type="purchase",  # or "delivery"
    default_filename="bill_13001.pdf",
    parent=self
)
```

**Returns:**
```python
{
    'file_path': str,
    'open_file': bool,
    'page_format': 'A4',
    'include_header': True,
    'include_footer': True,
    'quality': 'standard'
}
```

### PdfExportDialog

```python
dialog = PdfExportDialog(
    export_type="purchase",  # or "delivery"
    item_count=5,
    default_filename="bills_5_items.pdf",
    parent=self
)
```

**Returns:**
```python
{
    'file_path': str,
    'page_format': str,          # "A4", "Letter", "Legal"
    'include_header': bool,
    'include_footer': bool,
    'quality': str,              # "standard", "high"
    'open_file': bool,
    'open_folder': bool,
    'one_per_page': bool,        # If item_count > 1
    'include_summary': bool,     # If item_count > 1
}
```

### BatchExportProgressDialog

```python
progress = BatchExportProgressDialog(total_items=10, parent=self)
progress.show()

for idx, item in enumerate(items, 1):
    progress.update_progress(idx, item.name)
    # ... generate PDF ...
    if progress.result() == QMessageBox.StandardButton.Cancel:
        break

progress.set_completed()
```

## Helper Functions

### generate_export_filename()

```python
filename = generate_export_filename(
    export_type="purchase",    # "purchase" or "delivery"
    identifier="13001",        # Bill/invoice number
    timestamp=True             # Include timestamp
)
# Returns: "purchase_bill_13001_20250126_153045.pdf"
```

### format_file_size()

```python
size = format_file_size(1048576)
# Returns: "1.0 MB"
```

## Keyboard Shortcuts

| Shortcut      | Action                |
|---------------|-----------------------|
| Ctrl+P        | Export selected       |
| Ctrl+E        | Edit selected         |
| Ctrl+Shift+P  | Print receipt         |
| Delete        | Delete selected       |

## Signal Reference

### TableContextMenuMixin Signals

```python
# Single item selected
self.export_single_pdf.connect(handler)  # int (item_id)
self.view_details.connect(handler)       # int (item_id)
self.edit_item.connect(handler)          # int (item_id)
self.delete_item.connect(handler)        # int (item_id)
self.print_receipt.connect(handler)      # int (item_id)

# Multiple items selected
self.export_batch_pdf.connect(handler)   # list[int] (item_ids)
```

## Common Errors & Solutions

### Error: "Context menu doesn't appear"
**Solution:** Call `setup_table_context_menu(table, export_enabled=True)` after creating table

### Error: "Signals not firing"
**Solution:** Ensure mixin is in class definition: `class MyScreen(QWidget, TableContextMenuMixin)`

### Error: "Dialog doesn't open"
**Solution:** Check imports and pass `parent=self` to dialog constructor

### Error: "File path invalid"
**Solution:** Use `FileOperations.validate_path()` before attempting write

### Error: "File won't open"
**Solution:** Check file exists and default PDF viewer is installed

## Code Snippets

### Complete Minimal Screen

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget
from ui.widgets.context_menu_mixin import TableContextMenuMixin
from ui.dialogs.pdf_export_dialog import QuickPdfExportDialog
from ui.widgets.export_helpers import ExportNotification, generate_export_filename

class MinimalScreen(QWidget, TableContextMenuMixin):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.setup_table_context_menu(self.table, export_enabled=True)
        self.export_single_pdf.connect(self._export)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def _export(self, item_id):
        filename = generate_export_filename("item", str(item_id))
        dialog = QuickPdfExportDialog("item", filename, self)
        if dialog.exec():
            config = dialog.get_export_config()
            # TODO: Generate PDF
            ExportNotification.show_success(self, config['file_path'], 1)
```

### Add Export Button

```python
export_btn = QPushButton("Export to PDF")
export_btn.setProperty("success", True)
export_btn.clicked.connect(self._on_export_click)

def _on_export_click(self):
    selected = self.table.selectionModel().selectedRows()
    if not selected:
        QMessageBox.warning(self, "No Selection", "Select items to export")
        return

    ids = [self.table.item(row.row(), 0).data(Qt.ItemDataRole.UserRole)
           for row in selected]

    if len(ids) == 1:
        self.export_single_pdf.emit(ids[0])
    else:
        self.export_batch_pdf.emit(ids)
```

### Progress Dialog Example

```python
def _batch_export(self, item_ids, config):
    progress = BatchExportProgressDialog(len(item_ids), self)
    progress.show()

    try:
        for idx, item_id in enumerate(item_ids, 1):
            item = Service.get_by_id(self.db, item_id)
            progress.update_progress(idx, item.name)

            # TODO: Generate PDF for item

            if progress.result() == QMessageBox.StandardButton.Cancel:
                ExportNotification.show_info(self, "Cancelled", "Export cancelled")
                return

        progress.set_completed()
        ExportNotification.show_success(self, config['file_path'], len(item_ids))

    except Exception as e:
        progress.reject()
        ExportNotification.show_error(self, str(e))
```

## Styling Reference

### Button Properties

```python
# Success button (green)
btn.setProperty("success", True)

# Secondary button (gray)
btn.setProperty("secondary", True)

# Danger button (red)
btn.setProperty("danger", True)
```

### Dark Mode Colors

```python
COLORS = {
    'bg_primary': '#1e1e1e',
    'bg_secondary': '#2d2d2d',
    'primary': '#4da6ff',
    'success': '#4caf50',
    'error': '#f44336',
    'text_primary': '#e0e0e0',
}
```

## Testing Commands

```bash
# Run specific test
pytest tests/test_pdf_export.py -v

# Test with coverage
pytest --cov=ui/dialogs --cov=ui/widgets tests/

# Integration test
python -m ui.screens.purchase_list_with_export
```

## File Locations

```
ui/
├── dialogs/
│   └── pdf_export_dialog.py          # All dialogs
├── widgets/
│   ├── export_helpers.py              # Helper utilities
│   └── context_menu_mixin.py          # Context menu
└── screens/
    ├── purchase_list_with_export.py   # Enhanced purchase screen
    └── delivery_list_with_export.py   # Enhanced delivery screen
```

## Documentation Files

```
PDF_EXPORT_IMPLEMENTATION_GUIDE.md  # Complete technical guide
INTEGRATION_EXAMPLE.md              # Quick start examples
PDF_EXPORT_FEATURES.md              # Visual feature overview
PDF_EXPORT_ARCHITECTURE.md          # System architecture
PDF_EXPORT_SUMMARY.md               # Implementation summary
QUICK_REFERENCE.md                  # This file
```

## Next Steps After UI Implementation

1. **Install PDF Library**
   ```bash
   pip install reportlab
   ```

2. **Create PDF Generator**
   ```bash
   touch printing/pdf_generator.py
   ```

3. **Implement Generation**
   ```python
   class PdfGenerator:
       @staticmethod
       def generate_purchase_bill(bill, path, config):
           # ReportLab implementation
   ```

4. **Replace Placeholders**
   Search for "TODO: Implement" in export screens

5. **Test Complete Flow**
   - Export single item
   - Export batch
   - Verify PDF quality
   - Test on all platforms

## Support & Troubleshooting

1. Check console for error messages
2. Verify all imports are correct
3. Test with minimal example first
4. Review documentation files
5. Check file permissions
6. Verify PyQt6 version compatibility

## Version History

**v1.0** (2025-01-26)
- Initial implementation
- All UI components complete
- Documentation complete
- PDF generation pending
