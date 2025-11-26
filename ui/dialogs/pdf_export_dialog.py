"""
PDF Export Dialog
Dialog for exporting purchase bills and delivery invoices to PDF
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QGroupBox, QRadioButton, QButtonGroup,
    QFileDialog, QProgressBar, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from datetime import datetime
import os


class PdfExportDialog(QDialog):
    """Dialog for configuring and executing PDF export"""

    export_requested = pyqtSignal(dict)  # Emits export configuration

    def __init__(self, export_type="purchase", item_count=1, default_filename="", parent=None):
        """
        Initialize PDF export dialog

        Args:
            export_type: "purchase" or "delivery"
            item_count: Number of items being exported
            default_filename: Default filename suggestion
            parent: Parent widget
        """
        super().__init__(parent)
        self.export_type = export_type
        self.item_count = item_count
        self.default_filename = default_filename or self._generate_default_filename()
        self.selected_path = ""
        self.setup_ui()

    def _generate_default_filename(self) -> str:
        """Generate default filename based on export type"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.export_type == "purchase":
            if self.item_count > 1:
                return f"purchase_bills_{timestamp}.pdf"
            return f"purchase_bill_{timestamp}.pdf"
        else:
            if self.item_count > 1:
                return f"delivery_invoices_{timestamp}.pdf"
            return f"delivery_invoice_{timestamp}.pdf"

    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Export to PDF")
        self.setModal(True)
        self.setMinimumWidth(600)

        main_layout = QVBoxLayout()

        # Title
        title_text = f"Export {self.item_count} {'item' if self.item_count == 1 else 'items'} to PDF"
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        main_layout.addWidget(title)

        # Info label
        info_text = "Purchase Bills" if self.export_type == "purchase" else "Delivery Invoices"
        info = QLabel(f"Exporting: {info_text}")
        info.setProperty("secondary", True)
        main_layout.addWidget(info)

        # File location group
        location_group = self._create_location_group()
        main_layout.addWidget(location_group)

        # Export options group
        options_group = self._create_options_group()
        main_layout.addWidget(options_group)

        # Post-export options
        post_export_group = self._create_post_export_group()
        main_layout.addWidget(post_export_group)

        # Button group
        button_layout = self._create_button_group()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_location_group(self) -> QGroupBox:
        """Create file location selection group"""
        group = QGroupBox("Save Location")
        layout = QVBoxLayout()

        # File path display
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("File:"))

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select destination file...")
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_location)
        path_layout.addWidget(browse_btn)

        layout.addLayout(path_layout)

        # Quick location shortcuts
        shortcuts_layout = QHBoxLayout()
        shortcuts_layout.addWidget(QLabel("Quick locations:"))

        desktop_btn = QPushButton("Desktop")
        desktop_btn.setProperty("secondary", True)
        desktop_btn.clicked.connect(lambda: self._set_quick_location("Desktop"))
        shortcuts_layout.addWidget(desktop_btn)

        documents_btn = QPushButton("Documents")
        documents_btn.setProperty("secondary", True)
        documents_btn.clicked.connect(lambda: self._set_quick_location("Documents"))
        shortcuts_layout.addWidget(documents_btn)

        downloads_btn = QPushButton("Downloads")
        downloads_btn.setProperty("secondary", True)
        downloads_btn.clicked.connect(lambda: self._set_quick_location("Downloads"))
        shortcuts_layout.addWidget(downloads_btn)

        shortcuts_layout.addStretch()
        layout.addLayout(shortcuts_layout)

        group.setLayout(layout)
        return group

    def _create_options_group(self) -> QGroupBox:
        """Create export options group"""
        group = QGroupBox("Export Options")
        layout = QVBoxLayout()

        # Page format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Page Size:"))

        self.page_format = QComboBox()
        self.page_format.addItem("A4", "A4")
        self.page_format.addItem("Letter", "Letter")
        self.page_format.addItem("Legal", "Legal")
        format_layout.addWidget(self.page_format)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        # Include options
        self.include_header = QCheckBox("Include company header")
        self.include_header.setChecked(True)
        layout.addWidget(self.include_header)

        self.include_footer = QCheckBox("Include page footer (page numbers, export date)")
        self.include_footer.setChecked(True)
        layout.addWidget(self.include_footer)

        if self.item_count > 1:
            self.one_per_page = QCheckBox("One item per page")
            self.one_per_page.setChecked(True)
            layout.addWidget(self.one_per_page)

            self.include_summary = QCheckBox("Include summary page")
            self.include_summary.setChecked(True)
            layout.addWidget(self.include_summary)

        # Quality settings
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))

        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Standard (smaller file)", "standard")
        self.quality_combo.addItem("High (larger file)", "high")
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        layout.addLayout(quality_layout)

        group.setLayout(layout)
        return group

    def _create_post_export_group(self) -> QGroupBox:
        """Create post-export actions group"""
        group = QGroupBox("After Export")
        layout = QVBoxLayout()

        self.open_file = QCheckBox("Open PDF file after export")
        self.open_file.setChecked(True)
        layout.addWidget(self.open_file)

        self.open_folder = QCheckBox("Open containing folder")
        self.open_folder.setChecked(False)
        layout.addWidget(self.open_folder)

        group.setLayout(layout)
        return group

    def _create_button_group(self) -> QHBoxLayout:
        """Create dialog button group"""
        layout = QHBoxLayout()
        layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        export_btn = QPushButton("Export to PDF")
        export_btn.setProperty("success", True)
        export_btn.clicked.connect(self._handle_export)
        export_btn.setDefault(True)
        layout.addWidget(export_btn)

        return layout

    def _browse_location(self):
        """Open file browser to select save location"""
        suggested_name = self.default_filename
        default_dir = str(Path.home() / "Documents")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            str(Path(default_dir) / suggested_name),
            "PDF Files (*.pdf);;All Files (*.*)"
        )

        if file_path:
            # Ensure .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            self.selected_path = file_path
            self.path_input.setText(file_path)

    def _set_quick_location(self, location: str):
        """Set quick location (Desktop, Documents, Downloads)"""
        home = Path.home()
        if location == "Desktop":
            folder = home / "Desktop"
        elif location == "Documents":
            folder = home / "Documents"
        elif location == "Downloads":
            folder = home / "Downloads"
        else:
            return

        # Create folder if it doesn't exist
        folder.mkdir(parents=True, exist_ok=True)

        file_path = str(folder / self.default_filename)
        self.selected_path = file_path
        self.path_input.setText(file_path)

    def _handle_export(self):
        """Handle export button click"""
        if not self.selected_path:
            QMessageBox.warning(
                self,
                "No Location Selected",
                "Please select a location to save the PDF file."
            )
            return

        # Gather export configuration
        config = {
            'file_path': self.selected_path,
            'page_format': self.page_format.currentData(),
            'include_header': self.include_header.isChecked(),
            'include_footer': self.include_footer.isChecked(),
            'quality': self.quality_combo.currentData(),
            'open_file': self.open_file.isChecked(),
            'open_folder': self.open_folder.isChecked(),
        }

        # Add batch-specific options
        if self.item_count > 1:
            config['one_per_page'] = self.one_per_page.isChecked()
            config['include_summary'] = self.include_summary.isChecked()

        self.export_requested.emit(config)
        self.accept()

    def get_export_config(self) -> dict:
        """Get export configuration (alternative to signal)"""
        return {
            'file_path': self.selected_path,
            'page_format': self.page_format.currentData(),
            'include_header': self.include_header.isChecked(),
            'include_footer': self.include_footer.isChecked(),
            'quality': self.quality_combo.currentData(),
            'open_file': self.open_file.isChecked(),
            'open_folder': self.open_folder.isChecked(),
            'one_per_page': getattr(self, 'one_per_page', None) and self.one_per_page.isChecked(),
            'include_summary': getattr(self, 'include_summary', None) and self.include_summary.isChecked(),
        }


class BatchExportProgressDialog(QDialog):
    """Dialog showing progress for batch PDF export"""

    def __init__(self, total_items: int, parent=None):
        super().__init__(parent)
        self.total_items = total_items
        self.current_item = 0
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Exporting to PDF")
        self.setModal(True)
        self.setMinimumWidth(500)

        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Exporting to PDF")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.total_items)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(f"Preparing export... (0 of {self.total_items})")
        main_layout.addWidget(self.status_label)

        # Current item label
        self.current_label = QLabel("")
        self.current_label.setProperty("secondary", True)
        main_layout.addWidget(self.current_label)

        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("secondary", True)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def update_progress(self, current: int, current_item_name: str = ""):
        """Update progress bar and labels"""
        self.current_item = current
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Processing... ({current} of {self.total_items})")

        if current_item_name:
            self.current_label.setText(f"Current: {current_item_name}")

    def set_completed(self):
        """Set dialog to completed state"""
        self.progress_bar.setValue(self.total_items)
        self.status_label.setText(f"Export completed! ({self.total_items} items)")
        self.current_label.setText("PDF file created successfully")
        self.cancel_btn.setText("Close")


class QuickPdfExportDialog(QDialog):
    """Simplified quick export dialog with minimal options"""

    def __init__(self, export_type="purchase", default_filename="", parent=None):
        super().__init__(parent)
        self.export_type = export_type
        self.default_filename = default_filename
        self.selected_path = ""
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        self.setWindowTitle("Quick Export to PDF")
        self.setModal(True)
        self.setMinimumWidth(500)

        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Export to PDF")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(title)

        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Save as:"))

        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        file_layout.addWidget(self.path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_location)
        file_layout.addWidget(browse_btn)

        main_layout.addLayout(file_layout)

        # Quick options
        self.open_after = QCheckBox("Open PDF after export")
        self.open_after.setChecked(True)
        main_layout.addWidget(self.open_after)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        export_btn = QPushButton("Export")
        export_btn.setProperty("success", True)
        export_btn.clicked.connect(self._handle_export)
        export_btn.setDefault(True)
        button_layout.addWidget(export_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Auto-set to Documents folder
        self._set_default_location()

    def _set_default_location(self):
        """Set default location to Documents"""
        documents = Path.home() / "Documents"
        documents.mkdir(parents=True, exist_ok=True)
        self.selected_path = str(documents / self.default_filename)
        self.path_input.setText(self.selected_path)

    def _browse_location(self):
        """Open file browser"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            self.selected_path or str(Path.home() / "Documents" / self.default_filename),
            "PDF Files (*.pdf);;All Files (*.*)"
        )

        if file_path:
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            self.selected_path = file_path
            self.path_input.setText(file_path)

    def _handle_export(self):
        """Handle export"""
        if not self.selected_path:
            QMessageBox.warning(self, "Error", "Please select a save location")
            return
        self.accept()

    def get_export_config(self) -> dict:
        """Get export configuration"""
        return {
            'file_path': self.selected_path,
            'open_file': self.open_after.isChecked(),
            'page_format': 'A4',
            'include_header': True,
            'include_footer': True,
            'quality': 'standard'
        }
