"""
Receipt Export Dialog
Provides options to print receipt, save as PDF, or both
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QFileDialog, QMessageBox, QGroupBox, QRadioButton,
    QButtonGroup, QLineEdit
)
from PyQt5.QtCore import Qt
from pathlib import Path
import os


class ReceiptExportDialog(QDialog):
    """Dialog for selecting receipt output options"""

    def __init__(self, receipt_type: str, receipt_number: str, parent=None):
        """
        Initialize dialog

        Args:
            receipt_type: 'purchase' or 'delivery'
            receipt_number: Bill number or invoice number for display
            parent: Parent widget
        """
        super().__init__(parent)
        self.receipt_type = receipt_type
        self.receipt_number = receipt_number
        self.selected_action = None
        self.pdf_output_path = None

        self.setWindowTitle("Receipt Output Options")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout()

        # Title
        title_text = "Purchase Bill Receipt" if self.receipt_type == 'purchase' else "Delivery Invoice Receipt"
        title = QLabel(f"{title_text}: {self.receipt_number}")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel("Choose how to output the receipt:")
        instructions.setStyleSheet("color: #555; padding: 5px;")
        layout.addWidget(instructions)

        # Action selection group
        action_group = QGroupBox("Output Action")
        action_layout = QVBoxLayout()

        self.button_group = QButtonGroup(self)

        # Option 1: Print to Printer
        self.print_radio = QRadioButton("Print to Printer (Console)")
        self.print_radio.setStyleSheet("padding: 5px;")
        self.button_group.addButton(self.print_radio, 1)
        action_layout.addWidget(self.print_radio)

        print_note = QLabel("   Print receipt to console (printer integration pending)")
        print_note.setStyleSheet("color: #777; font-size: 10px; padding-left: 20px;")
        action_layout.addWidget(print_note)

        # Option 2: Save as PDF
        self.pdf_radio = QRadioButton("Save as PDF")
        self.pdf_radio.setStyleSheet("padding: 5px;")
        self.button_group.addButton(self.pdf_radio, 2)
        action_layout.addWidget(self.pdf_radio)

        pdf_note = QLabel("   Export receipt to PDF file with monospace formatting")
        pdf_note.setStyleSheet("color: #777; font-size: 10px; padding-left: 20px;")
        action_layout.addWidget(pdf_note)

        # Option 3: Both
        self.both_radio = QRadioButton("Both (Print & Save PDF)")
        self.both_radio.setStyleSheet("padding: 5px; font-weight: bold;")
        self.button_group.addButton(self.both_radio, 3)
        action_layout.addWidget(self.both_radio)

        both_note = QLabel("   Print to console and save PDF file")
        both_note.setStyleSheet("color: #777; font-size: 10px; padding-left: 20px;")
        action_layout.addWidget(both_note)

        # Set default selection
        self.both_radio.setChecked(True)

        action_group.setLayout(action_layout)
        layout.addWidget(action_group)

        # PDF output path section
        pdf_path_group = QGroupBox("PDF Output Location (Optional)")
        pdf_path_layout = QVBoxLayout()

        path_info = QLabel("Leave empty for auto-generated filename in exports/receipts/")
        path_info.setStyleSheet("color: #555; font-size: 10px; padding: 5px;")
        pdf_path_layout.addWidget(path_info)

        path_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Auto-generated path...")
        self.path_input.setReadOnly(True)
        path_row.addWidget(self.path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output_path)
        path_row.addWidget(browse_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_output_path)
        path_row.addWidget(clear_btn)

        pdf_path_layout.addLayout(path_row)
        pdf_path_group.setLayout(pdf_path_layout)
        layout.addWidget(pdf_path_group)

        # Button row
        button_layout = QHBoxLayout()

        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.ok_button.clicked.connect(self.accept_action)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setMinimumWidth(500)

    def browse_output_path(self):
        """Open file dialog to choose PDF output path"""
        default_dir = os.path.join(os.getcwd(), 'exports', 'receipts')

        if self.receipt_type == 'purchase':
            default_filename = f"receipt_purchase_{self.receipt_number}.pdf"
        else:
            default_filename = f"receipt_delivery_{self.receipt_number}.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Receipt PDF",
            os.path.join(default_dir, default_filename),
            "PDF Files (*.pdf)"
        )

        if file_path:
            self.path_input.setText(file_path)
            self.pdf_output_path = file_path

    def clear_output_path(self):
        """Clear custom output path"""
        self.path_input.clear()
        self.pdf_output_path = None

    def accept_action(self):
        """Accept dialog and store selected action"""
        selected_id = self.button_group.checkedId()

        if selected_id == 1:
            self.selected_action = 'print'
        elif selected_id == 2:
            self.selected_action = 'pdf'
        elif selected_id == 3:
            self.selected_action = 'both'
        else:
            QMessageBox.warning(self, "Warning", "Please select an action")
            return

        # Get custom path if provided
        if self.path_input.text().strip():
            self.pdf_output_path = self.path_input.text().strip()

        self.accept()

    def get_action(self) -> str:
        """
        Get selected action

        Returns:
            'print', 'pdf', or 'both'
        """
        return self.selected_action

    def get_pdf_path(self) -> str:
        """
        Get custom PDF output path

        Returns:
            Path string or None for auto-generated
        """
        return self.pdf_output_path

    def should_print(self) -> bool:
        """Check if should print to printer"""
        return self.selected_action in ['print', 'both']

    def should_export_pdf(self) -> bool:
        """Check if should export to PDF"""
        return self.selected_action in ['pdf', 'both']
