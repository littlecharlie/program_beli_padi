# PDF Export Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────┐         ┌────────────────────┐             │
│  │  Purchase List     │         │  Delivery List     │             │
│  │  Screen            │         │  Screen            │             │
│  │                    │         │                    │             │
│  │  - Table Widget    │         │  - Table Widget    │             │
│  │  - Export Buttons  │         │  - Export Buttons  │             │
│  │  - Context Menu    │         │  - Context Menu    │             │
│  └────────┬───────────┘         └────────┬───────────┘             │
│           │                              │                          │
│           │    Uses Mixin                │                          │
│           ▼                              ▼                          │
│  ┌──────────────────────────────────────────────┐                  │
│  │   TableContextMenuMixin                      │                  │
│  │   - setup_table_context_menu()               │                  │
│  │   - Signals: export_single_pdf               │                  │
│  │              export_batch_pdf                │                  │
│  │              view_details, edit, delete      │                  │
│  └──────────────────┬───────────────────────────┘                  │
│                     │                                               │
└─────────────────────┼───────────────────────────────────────────────┘
                      │
                      │ Emits Signals
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DIALOG & HELPER LAYER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  EXPORT DIALOGS (pdf_export_dialog.py)                      │   │
│  │                                                              │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐  │   │
│  │  │ PdfExportDialog  │  │ QuickPdf         │  │ Progress │  │   │
│  │  │                  │  │ ExportDialog     │  │ Dialog   │  │   │
│  │  │ - Full options   │  │ - Simplified     │  │ - Batch  │  │   │
│  │  │ - Page format    │  │ - Quick export   │  │ - Track  │  │   │
│  │  │ - Quality        │  │ - Auto location  │  │ - Cancel │  │   │
│  │  │ - Headers        │  │                  │  │          │  │   │
│  │  │ - Batch opts     │  │                  │  │          │  │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  EXPORT HELPERS (export_helpers.py)                         │   │
│  │                                                              │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐  │   │
│  │  │ Export           │  │ FileOperations   │  │ Toast    │  │   │
│  │  │ Notification     │  │                  │  │ Notify   │  │   │
│  │  │ - show_success() │  │ - open_file()    │  │ - show() │  │   │
│  │  │ - show_error()   │  │ - open_folder()  │  │          │  │   │
│  │  │ - show_warning() │  │ - validate_path()│  │          │  │   │
│  │  │ - confirm_       │  │ - unique_name()  │  │          │  │   │
│  │  │   overwrite()    │  │                  │  │          │  │   │
│  │  └──────────────────┘  └──────────────────┘  └──────────┘  │   │
│  │                                                              │   │
│  │  Helper Functions:                                           │   │
│  │  - generate_export_filename()                                │   │
│  │  - format_file_size()                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │ Calls
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PDF GENERATION LAYER (TODO)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  PDF GENERATOR (printing/pdf_generator.py) - NOT IMPLEMENTED│   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │ PdfGenerator                                         │   │   │
│  │  │                                                      │   │   │
│  │  │  - generate_purchase_bill(bill, path, config)       │   │   │
│  │  │  - generate_delivery_invoice(invoice, path, config) │   │   │
│  │  │  - generate_batch_pdf(items, path, config)          │   │   │
│  │  │  - add_header(pdf, company_info)                    │   │   │
│  │  │  - add_footer(pdf, page_num, date)                  │   │   │
│  │  │  - format_bill_content(bill)                        │   │   │
│  │  │  - format_invoice_content(invoice)                  │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  PDF LIBRARY (reportlab / PyPDF2)                           │   │
│  │  - Canvas, Document generation                              │   │
│  │  - Text formatting, tables                                  │   │
│  │  - Page layout and styling                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │ Writes to
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       FILE SYSTEM LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Desktop/Documents/Downloads/                                        │
│  └── purchase_bill_13001_20250126.pdf                              │
│  └── delivery_invoice_01001_20250126.pdf                           │
│  └── purchase_bills_5_items_20250126.pdf                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

### Flow 1: Single Item Export

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  User    │     │   Screen     │     │    Dialog    │     │  Helper  │
└────┬─────┘     └──────┬───────┘     └──────┬───────┘     └────┬─────┘
     │                  │                    │                   │
     │ Right-click      │                    │                   │
     │ "Export as PDF"  │                    │                   │
     ├─────────────────>│                    │                   │
     │                  │                    │                   │
     │                  │ Show Quick Dialog  │                   │
     │                  ├───────────────────>│                   │
     │                  │                    │                   │
     │  Configure       │                    │                   │
     │  Click Export    │                    │                   │
     ├─────────────────────────────────────>│                   │
     │                  │                    │                   │
     │                  │                    │ get_export_config()│
     │                  │                    ├──────────────────>│
     │                  │                    │                   │
     │                  │  config dict       │                   │
     │                  │<───────────────────┤                   │
     │                  │                    │                   │
     │                  │ Generate PDF       │                   │
     │                  │ (placeholder)      │                   │
     │                  ├──────────────────────────────────────> │
     │                  │                    │                   │
     │                  │                    │                   │
     │                  │<───────────────────────────────────────┤
     │                  │  success/failure   │                   │
     │                  │                    │                   │
     │                  │                    │  show_success()   │
     │                  ├───────────────────────────────────────>│
     │                  │                    │                   │
     │  Notification    │                    │                   │
     │<─────────────────┤                    │                   │
     │                  │                    │                   │
     │                  │                    │  open_file()      │
     │                  ├───────────────────────────────────────>│
     │                  │                    │                   │
     │  PDF opens       │                    │                   │
     │<─────────────────────────────────────────────────────────┤
     │                  │                    │                   │
```

### Flow 2: Batch Export with Progress

```
┌──────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌─────────┐
│  User    │  │  Screen    │  │   Dialog   │  │ Progress │  │ Helper  │
└────┬─────┘  └─────┬──────┘  └─────┬──────┘  └────┬─────┘  └────┬────┘
     │              │               │              │             │
     │ Select 5     │               │              │             │
     │ Right-click  │               │              │             │
     │ "Export N"   │               │              │             │
     ├─────────────>│               │              │             │
     │              │               │              │             │
     │              │ Show Full     │              │             │
     │              │ Dialog        │              │             │
     │              ├──────────────>│              │             │
     │              │               │              │             │
     │  Configure   │               │              │             │
     │  Click Export│               │              │             │
     ├─────────────────────────────>│              │             │
     │              │               │              │             │
     │              │               │ Show Progress│             │
     │              │               ├─────────────>│             │
     │              │               │              │             │
     │              │  For each item│              │             │
     │              │  ┌───────────┐│              │             │
     │              │  │Generate PDF││              │             │
     │              │  │Update %    ││              │             │
     │              │  │            │├──update────>│             │
     │              │  │            ││              │             │
     │              │  │Check cancel││              │             │
     │              │  │<───────────┼┼──────────────┤             │
     │              │  └───────────┘│              │             │
     │              │               │              │             │
     │              │               │ set_completed│             │
     │              │               ├─────────────>│             │
     │              │               │              │             │
     │              │               │              │ show_success│
     │              │               ├─────────────────────────────>
     │              │               │              │             │
     │  Success     │               │              │             │
     │<─────────────────────────────┴──────────────┴─────────────┤
     │              │               │              │             │
```

## Class Hierarchy

```
QWidget
└── TableContextMenuMixin (Mixin)
    ├── PurchaseListScreenWithExport
    └── DeliveryListScreenWithExport

QDialog
├── PdfExportDialog
├── QuickPdfExportDialog
└── BatchExportProgressDialog

Object
├── ExportNotification (Static utility class)
├── FileOperations (Static utility class)
└── PdfGenerator (TODO - Not implemented)
```

## Signal-Slot Connections

```
TableContextMenuMixin Signals:
┌─────────────────────────┐
│ export_single_pdf(int)  ├──┐
│ export_batch_pdf(list)  ├──┤
│ view_details(int)       ├──┤
│ edit_item(int)          ├──┼──> Connected in Screen.__init__()
│ delete_item(int)        ├──┤
│ print_receipt(int)      ├──┘
└─────────────────────────┘

PdfExportDialog Signals:
┌─────────────────────────┐
│ export_requested(dict)  ├──> Optional, can use get_export_config()
└─────────────────────────┘

Screen Slots:
┌──────────────────────────────┐
│ _export_single_bill(int)     │<── Handles single export
│ _export_batch_bills(list)    │<── Handles batch export
│ _export_selected()           │<── Handles button click
│ _export_all()                │<── Handles export all
└──────────────────────────────┘
```

## Data Flow

```
User Selection
      │
      ▼
┌─────────────────┐
│  Table Widget   │
│  - Selected IDs │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│  Context Menu    │
│  or Button Click │
└────────┬─────────┘
         │
         ▼
┌─────────────────────┐
│  Export Handler     │
│  - Single or Batch  │
│  - Get item(s)      │
└────────┬────────────┘
         │
         ▼
┌────────────────────┐
│  Export Dialog     │
│  - User config     │
│  - File location   │
└────────┬───────────┘
         │
         ▼
┌─────────────────────┐
│  PDF Generator      │
│  (TODO: Implement)  │
│  - Create PDF       │
│  - Apply config     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  File System        │
│  - Write PDF        │
│  - Verify           │
└────────┬────────────┘
         │
         ▼
┌──────────────────────┐
│  Post-Export Actions │
│  - Notification      │
│  - Open file         │
│  - Open folder       │
└──────────────────────┘
```

## File Dependencies

```
purchase_list_with_export.py
├── imports from PyQt6.QtWidgets
├── imports from services (PurchaseService, ConfigService)
├── imports from printing (PurchaseReceiptFormatter)
└── imports from ui
    ├── ui.dialogs.pdf_export_dialog
    │   ├── PdfExportDialog
    │   ├── QuickPdfExportDialog
    │   └── BatchExportProgressDialog
    ├── ui.widgets.export_helpers
    │   ├── ExportNotification
    │   ├── FileOperations
    │   └── generate_export_filename()
    └── ui.widgets.context_menu_mixin
        └── TableContextMenuMixin

delivery_list_with_export.py
└── (Same structure as purchase_list_with_export.py)
```

## Configuration Dictionary Structure

```python
config = {
    # Required
    'file_path': str,              # "/path/to/file.pdf"

    # Page settings
    'page_format': str,            # "A4" | "Letter" | "Legal"
    'quality': str,                # "standard" | "high"

    # Content options
    'include_header': bool,        # True | False
    'include_footer': bool,        # True | False

    # Batch-specific (optional)
    'one_per_page': bool,          # True | False
    'include_summary': bool,       # True | False

    # Post-export actions
    'open_file': bool,             # True | False
    'open_folder': bool,           # True | False
}
```

## Error Handling Flow

```
Try Export
    │
    ├─> File Path Invalid
    │   └─> validate_path() returns False
    │       └─> Show error notification
    │           └─> Return to dialog
    │
    ├─> File Exists
    │   └─> confirm_overwrite() dialog
    │       ├─> User says No
    │       │   └─> Return to dialog
    │       └─> User says Yes
    │           └─> Continue
    │
    ├─> Generation Fails
    │   └─> Exception caught
    │       └─> show_error(exception message)
    │           └─> Log error
    │               └─> User can retry
    │
    └─> Success
        └─> show_success(file_path, count)
            └─> Post-export actions
                ├─> open_file() if requested
                └─> open_folder() if requested
```

## Extension Points

### Adding New Export Type

1. Create new export type in helpers:
   ```python
   def generate_export_filename(export_type: str, ...):
       if export_type == "my_new_type":
           # Custom filename logic
   ```

2. Create export handler in screen:
   ```python
   def _export_my_type(self, item_id):
       dialog = QuickPdfExportDialog("my_type", filename, self)
       # ... handle export
   ```

3. Connect to UI action:
   ```python
   my_export_btn.clicked.connect(self._export_my_type)
   ```

### Adding New Export Option

1. Add UI element in dialog:
   ```python
   self.my_option = QCheckBox("My new option")
   layout.addWidget(self.my_option)
   ```

2. Include in config:
   ```python
   config['my_option'] = self.my_option.isChecked()
   ```

3. Use in PDF generator:
   ```python
   if config.get('my_option'):
       # Apply option
   ```

### Adding New Post-Export Action

1. Add checkbox in dialog
2. Add to config dict
3. Implement in export handler:
   ```python
   if config.get('my_action'):
       self._perform_my_action(file_path)
   ```

## Testing Strategy

### Unit Tests
- Helper functions (filename generation, file size formatting)
- Validation functions (path validation, file existence)
- Notification creation

### Integration Tests
- Dialog opening and closing
- Signal-slot connections
- Config dictionary creation
- File operations

### UI Tests
- Context menu appearance
- Button clicks
- Keyboard shortcuts
- Progress dialog updates

### End-to-End Tests
- Complete export workflow
- Multiple items export
- Error scenarios
- Cancel operations

## Performance Optimization

### Current Optimizations
- Lazy loading of dialogs (create on demand)
- Non-blocking progress updates
- Stream to file (when PDF gen implemented)
- Cancel support for long operations

### Future Optimizations
- Background thread for PDF generation
- Batch processing with queue
- Incremental progress updates
- Memory pooling for large batches

## Security Considerations

### Input Validation
- File path validation
- Directory permissions check
- Filename sanitization
- Extension enforcement (.pdf)

### Data Privacy
- No sensitive data in filenames
- Secure file permissions
- No external network calls
- Local file storage only

## Maintenance Notes

### Code Metrics
- Total lines: ~2000
- Cyclomatic complexity: Medium
- Test coverage: 0% (needs implementation)
- Documentation: 100%

### Known Issues
- PDF generation not implemented (placeholder only)
- Cross-platform file opening needs testing
- Large batch performance untested

### Future Improvements
- Add PDF preview before export
- Email export integration
- Cloud storage upload
- Template system for layouts
- Scheduled/automated exports
