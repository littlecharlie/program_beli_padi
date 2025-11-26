# PDF Export Integration - Quick Start Example

## Overview

This guide shows you how to quickly integrate PDF export into your existing screens in 5 simple steps.

## Quick Integration (5 Steps)

### Step 1: Update Your Screen Class

Add the `TableContextMenuMixin` to your screen class:

```python
# Before
from PyQt6.QtWidgets import QWidget

class PurchaseListScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ...

# After
from PyQt6.QtWidgets import QWidget
from ui.widgets.context_menu_mixin import TableContextMenuMixin

class PurchaseListScreen(QWidget, TableContextMenuMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ...
```

### Step 2: Setup Context Menu

In your `setup_ui()` method, after creating your table:

```python
def setup_ui(self):
    # ... existing table creation code ...

    self.bills_table = QTableWidget()
    # ... table configuration ...

    # Add this line - setup context menu
    self.setup_table_context_menu(self.bills_table, export_enabled=True)

    # Connect the export signals
    self.export_single_pdf.connect(self._handle_single_export)
    self.export_batch_pdf.connect(self._handle_batch_export)
```

### Step 3: Add Export Button to UI

Add an export button to your toolbar or button group:

```python
def _create_button_group(self):
    layout = QHBoxLayout()

    # ... existing buttons ...

    # Add export button
    export_btn = QPushButton("Export to PDF")
    export_btn.setProperty("success", True)
    export_btn.setToolTip("Export selected items to PDF")
    export_btn.clicked.connect(self._export_selected_items)
    layout.addWidget(export_btn)

    # ... rest of layout ...
    return layout
```

### Step 4: Implement Export Handlers

Add these methods to your screen class:

```python
from ui.dialogs.pdf_export_dialog import QuickPdfExportDialog, PdfExportDialog
from ui.widgets.export_helpers import (
    ExportNotification, FileOperations, generate_export_filename
)

def _export_selected_items(self):
    """Handle export button click"""
    selected_rows = self.bills_table.selectionModel().selectedRows()
    if not selected_rows:
        QMessageBox.warning(self, "No Selection", "Please select items to export")
        return

    # Get selected IDs
    item_ids = []
    for row in selected_rows:
        item = self.bills_table.item(row.row(), 0)
        if item:
            item_id = item.data(Qt.ItemDataRole.UserRole)
            if item_id:
                item_ids.append(item_id)

    # Single or batch
    if len(item_ids) == 1:
        self._handle_single_export(item_ids[0])
    else:
        self._handle_batch_export(item_ids)

def _handle_single_export(self, item_id: int):
    """Export single item to PDF"""
    # Get the item from database
    item = PurchaseService.get_by_id(self.db, item_id)
    if not item:
        return

    # Generate filename
    filename = generate_export_filename("purchase", item.bill_number)

    # Show quick export dialog
    dialog = QuickPdfExportDialog("purchase", filename, self)
    if dialog.exec():
        config = dialog.get_export_config()

        try:
            # TODO: Replace with actual PDF generation
            file_path = config['file_path']

            # Placeholder - create empty file
            from pathlib import Path
            Path(file_path).touch()

            # Show success
            ExportNotification.show_success(self, file_path, 1)

            # Post-export actions
            if config.get('open_file'):
                FileOperations.open_file(file_path)

        except Exception as e:
            ExportNotification.show_error(self, str(e))

def _handle_batch_export(self, item_ids: list):
    """Export multiple items to PDF"""
    filename = generate_export_filename("purchase", f"{len(item_ids)}_items")

    # Show full export dialog with options
    dialog = PdfExportDialog("purchase", len(item_ids), filename, self)
    if dialog.exec():
        config = dialog.get_export_config()

        try:
            # TODO: Replace with actual PDF generation
            file_path = config['file_path']

            # Placeholder - create empty file
            from pathlib import Path
            Path(file_path).touch()

            # Show success
            ExportNotification.show_success(self, file_path, len(item_ids))

            # Post-export actions
            if config.get('open_file'):
                FileOperations.open_file(file_path)

        except Exception as e:
            ExportNotification.show_error(self, str(e))
```

### Step 5: Test It!

Run your application and test:

1. **Right-click on a table row** → See "Export as PDF" in context menu
2. **Select multiple rows and right-click** → See "Export N items as PDF"
3. **Click the "Export to PDF" button** → Dialog opens
4. **Try keyboard shortcut** → Ctrl+P to export selected

## Complete Minimal Example

Here's a complete minimal screen with PDF export:

```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from ui.widgets.context_menu_mixin import TableContextMenuMixin
from ui.dialogs.pdf_export_dialog import QuickPdfExportDialog, PdfExportDialog
from ui.widgets.export_helpers import (
    ExportNotification, FileOperations, generate_export_filename
)

class MinimalExportScreen(QWidget, TableContextMenuMixin):
    """Minimal screen demonstrating PDF export integration"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Export button
        export_btn = QPushButton("Export to PDF")
        export_btn.setProperty("success", True)
        export_btn.clicked.connect(self._export_selected)
        layout.addWidget(export_btn)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Value"])

        # Setup context menu
        self.setup_table_context_menu(self.table, export_enabled=True)

        # Connect signals
        self.export_single_pdf.connect(self._handle_single_export)
        self.export_batch_pdf.connect(self._handle_batch_export)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        """Load sample data"""
        data = [
            (1, "Item A", "100.00"),
            (2, "Item B", "200.00"),
            (3, "Item C", "300.00"),
        ]

        self.table.setRowCount(len(data))
        for row, (id, name, value) in enumerate(data):
            item = QTableWidgetItem(str(id))
            item.setData(Qt.ItemDataRole.UserRole, id)
            self.table.setItem(row, 0, item)
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(value))

    def _export_selected(self):
        """Export selected items"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Warning", "Select items to export")
            return

        ids = [self.table.item(row.row(), 0).data(Qt.ItemDataRole.UserRole)
               for row in selected]

        if len(ids) == 1:
            self._handle_single_export(ids[0])
        else:
            self._handle_batch_export(ids)

    def _handle_single_export(self, item_id: int):
        """Export single item"""
        filename = generate_export_filename("item", str(item_id))
        dialog = QuickPdfExportDialog("item", filename, self)

        if dialog.exec():
            config = dialog.get_export_config()
            self._generate_pdf(item_id, config)

    def _handle_batch_export(self, item_ids: list):
        """Export multiple items"""
        filename = generate_export_filename("item", f"{len(item_ids)}_items")
        dialog = PdfExportDialog("item", len(item_ids), filename, self)

        if dialog.exec():
            config = dialog.get_export_config()
            self._generate_batch_pdf(item_ids, config)

    def _generate_pdf(self, item_id, config):
        """Generate PDF for single item"""
        try:
            from pathlib import Path
            file_path = config['file_path']

            # TODO: Actual PDF generation here
            Path(file_path).touch()  # Placeholder

            ExportNotification.show_success(self, file_path, 1)

            if config.get('open_file'):
                FileOperations.open_file(file_path)

        except Exception as e:
            ExportNotification.show_error(self, str(e))

    def _generate_batch_pdf(self, item_ids, config):
        """Generate PDF for multiple items"""
        try:
            from pathlib import Path
            file_path = config['file_path']

            # TODO: Actual PDF generation here
            Path(file_path).touch()  # Placeholder

            ExportNotification.show_success(self, file_path, len(item_ids))

            if config.get('open_file'):
                FileOperations.open_file(file_path)

        except Exception as e:
            ExportNotification.show_error(self, str(e))
```

## Using the Pre-Built Enhanced Screens

The easiest way is to use the pre-built enhanced screens:

### In `main_window.py`:

```python
# Replace old imports
from ui.screens.purchase_list_with_export import PurchaseListScreenWithExport
from ui.screens.delivery_list_with_export import DeliveryListScreenWithExport

# Use in your __init__:
def __init__(self):
    super().__init__()

    # Create enhanced screens with export
    self.purchase_list_screen = PurchaseListScreenWithExport(self)
    self.delivery_list_screen = DeliveryListScreenWithExport(self)

    # Add to your stacked widget or tab widget
    self.stacked_widget.addWidget(self.purchase_list_screen)
    self.stacked_widget.addWidget(self.delivery_list_screen)
```

That's it! The screens now have:
- Right-click context menu with export options
- Export toolbar buttons
- Keyboard shortcuts (Ctrl+P)
- Batch export support
- Progress tracking
- Success/error notifications
- Auto-open capabilities

## Customization

### Custom Export Handler

If you need custom export logic:

```python
def _handle_single_export(self, item_id: int):
    """Custom export with validation"""
    item = self.service.get_by_id(self.db, item_id)

    # Custom validation
    if item.is_delivered:
        QMessageBox.warning(self, "Warning", "Cannot export delivered items")
        return

    # Custom filename format
    filename = f"BILL_{item.bill_number}_{item.farmer.name}.pdf"

    # Continue with standard export
    dialog = QuickPdfExportDialog("purchase", filename, self)
    # ...
```

### Custom Export Options

Add custom options to the dialog:

```python
dialog = PdfExportDialog("purchase", 1, filename, self)

# After exec, add custom processing
if dialog.exec():
    config = dialog.get_export_config()

    # Add custom options
    config['include_photos'] = True
    config['watermark'] = "DRAFT"

    self._generate_pdf(item, config)
```

### Custom Notifications

Use custom notification styles:

```python
# Custom success message
QMessageBox.information(
    self,
    "Export Successful",
    f"Exported {count} items to:\n{file_path}\n\n"
    f"File size: {format_file_size(file_size)}"
)

# Custom error with details
QMessageBox.critical(
    self,
    "Export Failed",
    f"Failed to export items:\n\n"
    f"Error: {error_message}\n\n"
    f"Please check:\n"
    f"- File permissions\n"
    f"- Available disk space\n"
    f"- Valid file path"
)
```

## Troubleshooting

### Context menu doesn't appear
- Check: `self.setup_table_context_menu(self.table, export_enabled=True)` is called
- Check: Table has `CustomContextMenu` policy

### Export button does nothing
- Check: Signal is connected: `export_btn.clicked.connect(self._export_selected)`
- Check: Method is defined in your class

### Dialog doesn't open
- Check: Import statements are correct
- Check: Parent is passed to dialog: `dialog = QuickPdfExportDialog(..., parent=self)`

### File doesn't open after export
- Check: Platform-specific file opening is supported
- Check: File actually exists at the path
- Check: Default PDF viewer is installed

### Signals not working
- Check: Mixin is included: `class MyScreen(QWidget, TableContextMenuMixin)`
- Check: Signals are connected after `setup_table_context_menu()` call

## Next Steps

1. **Implement PDF Generation**: Replace placeholder with actual PDF library
2. **Add Templates**: Create different PDF layouts
3. **Add Preview**: Show PDF preview before export
4. **Add Settings**: Let users configure default export options
5. **Add History**: Track exported files for re-export

## Resources

- Main Guide: `PDF_EXPORT_IMPLEMENTATION_GUIDE.md`
- Enhanced Purchase Screen: `ui/screens/purchase_list_with_export.py`
- Enhanced Delivery Screen: `ui/screens/delivery_list_with_export.py`
- Export Dialogs: `ui/dialogs/pdf_export_dialog.py`
- Helper Functions: `ui/widgets/export_helpers.py`
- Context Menu: `ui/widgets/context_menu_mixin.py`
