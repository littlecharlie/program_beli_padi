"""
Purchase Bill List Screen
View, search, and manage purchase bills
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QDateEdit, QComboBox, QSpinBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime, timedelta
from config.database import get_db
from services.purchase_service import PurchaseService
from printing.purchase_receipt import PurchaseReceiptFormatter
from services.config_service import ConfigService
from services.receipt_pdf_service import ReceiptPdfService, ReceiptPdfError
from ui.dialogs.receipt_export_dialog import ReceiptExportDialog
# Edit functionality disabled per user request
# from ui.dialogs.purchase_edit_dialog import PurchaseEditDialog
import os


class PurchaseListScreen(QWidget):
    """Screen for viewing and managing purchase bills"""

    # Signals
    bill_selected = pyqtSignal(int)  # bill_id
    create_purchase_bill = pyqtSignal()  # Signal to create new purchase bill

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.setup_ui()
        self.load_bills()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Purchase Bills")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Search/Filter Group
        search_layout = self._create_search_group()
        main_layout.addLayout(search_layout)

        # Bills Table
        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(9)
        self.bills_table.setHorizontalHeaderLabels([
            "Bill No",
            "Date",
            "Farmer Name",
            "Net Weight",
            "Total Payment",
            "Status",
            "Truck",
            "Created By",
            "Actions"
        ])
        self.bills_table.setColumnWidth(0, 80)
        self.bills_table.setColumnWidth(1, 120)
        self.bills_table.setColumnWidth(2, 150)
        self.bills_table.setColumnWidth(3, 100)
        self.bills_table.setColumnWidth(4, 120)
        self.bills_table.setColumnWidth(5, 80)
        self.bills_table.setColumnWidth(6, 100)
        self.bills_table.setColumnWidth(7, 100)
        self.bills_table.setColumnWidth(8, 100)
        self.bills_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self.bills_table.setSelectionMode(
            QTableWidget.SingleSelection
        )
        # Disable cell editing - users must use the Edit button
        self.bills_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        main_layout.addWidget(self.bills_table)

        # Statistics Group
        stats_layout = self._create_stats_group()
        main_layout.addLayout(stats_layout)

        # Button Group
        button_layout = self._create_button_group()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_search_group(self) -> QHBoxLayout:
        """Create search and filter group"""
        layout = QHBoxLayout()

        # Search by bill number or farmer name
        layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Bill number or farmer name")
        self.search_input.returnPressed.connect(self.search_bills)
        layout.addWidget(self.search_input)

        # Filter by status
        layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("All", "all")
        self.status_combo.addItem("Pending", "pending")
        self.status_combo.addItem("Delivered", "delivered")
        self.status_combo.currentIndexChanged.connect(self.apply_filters)
        layout.addWidget(self.status_combo)

        # Date range
        layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.dateChanged.connect(self.apply_filters)
        layout.addWidget(self.from_date)

        layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.dateChanged.connect(self.apply_filters)
        layout.addWidget(self.to_date)

        # Search button
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_bills)
        layout.addWidget(search_btn)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_bills)
        layout.addWidget(refresh_btn)

        layout.addStretch()

        return layout

    def _create_stats_group(self) -> QHBoxLayout:
        """Create statistics group"""
        layout = QHBoxLayout()

        stats = PurchaseService.get_statistics(self.db)

        layout.addWidget(QLabel(f"Total Bills: {stats['total_bills']}"))
        layout.addWidget(QLabel(f"Pending: {stats['pending_bills']}"))
        layout.addWidget(QLabel(f"Delivered: {stats['delivered_bills']}"))
        layout.addWidget(QLabel(f"Total Weight: {stats['total_weight']:,.2f} kg"))
        layout.addWidget(QLabel(f"Total Payment: RM {stats['total_payment']:,.2f}"))
        layout.addStretch()

        return layout

    def _create_button_group(self) -> QHBoxLayout:
        """Create button group"""
        layout = QHBoxLayout()

        # New Purchase Bill button - primary action
        self.new_bill_btn = QPushButton("New Purchase Bill")
        self.new_bill_btn.setStyleSheet(
            "background-color: #28a745; color: white; font-weight: bold; padding: 8px 16px;"
        )
        self.new_bill_btn.clicked.connect(self._on_create_purchase_bill)

        self.print_btn = QPushButton("Print Receipt")
        self.print_btn.clicked.connect(self.print_receipt)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self.delete_btn.clicked.connect(self.delete_bill)

        layout.addWidget(self.new_bill_btn)
        layout.addWidget(self.print_btn)
        layout.addWidget(self.delete_btn)
        layout.addStretch()

        return layout

    def _create_table_button(self, text: str, style: str = None) -> QPushButton:
        """
        Create a button sized to fit table row height

        Args:
            text: Button text
            style: Optional custom stylesheet

        Returns:
            QPushButton configured for table cell use
        """
        btn = QPushButton(text)

        # Compact button styling that overrides global button styles
        base_style = """
            QPushButton {
                padding: 4px 12px;
                min-height: 20px;
                max-height: 24px;
                font-size: 9pt;
                border-radius: 3px;
                font-weight: 600;
            }
        """

        if style:
            # Merge custom style with base style
            btn.setStyleSheet(base_style + style)
        else:
            # Default blue button for table actions
            btn.setStyleSheet(base_style + """
                QPushButton {
                    background-color: #4da6ff;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #66b3ff;
                }
                QPushButton:pressed {
                    background-color: #3d8ae6;
                }
            """)

        return btn

    def _on_create_purchase_bill(self):
        """Handle create new purchase bill button click"""
        self.create_purchase_bill.emit()

    def load_bills(self):
        """Load all bills into table"""
        bills = PurchaseService.get_all(self.db)
        self.populate_table(bills)

    def populate_table(self, bills):
        """Populate table with bills"""
        self.bills_table.setRowCount(len(bills))

        for row, bill in enumerate(bills):
            # Set row height for consistent button sizing
            self.bills_table.setRowHeight(row, 44)

            # Bill number
            item = QTableWidgetItem(bill.bill_number)
            item.setData(Qt.UserRole, bill.id)
            self.bills_table.setItem(row, 0, item)

            # Date
            date_str = bill.bill_date.strftime("%d/%m/%Y %H:%M")
            self.bills_table.setItem(row, 1, QTableWidgetItem(date_str))

            # Farmer name
            farmer_name = bill.farmer.name if bill.farmer else "Unknown"
            self.bills_table.setItem(row, 2, QTableWidgetItem(farmer_name))

            # Net weight
            net_weight_str = f"{float(bill.net_weight):,.2f} kg"
            self.bills_table.setItem(row, 3, QTableWidgetItem(net_weight_str))

            # Total payment
            payment_str = f"RM {float(bill.total_payment):,.2f}"
            self.bills_table.setItem(row, 4, QTableWidgetItem(payment_str))

            # Status
            status = "Delivered" if bill.is_delivered else "Pending"
            self.bills_table.setItem(row, 5, QTableWidgetItem(status))

            # Truck
            truck_number = bill.truck.truck_number if bill.truck else "Unknown"
            self.bills_table.setItem(row, 6, QTableWidgetItem(truck_number))

            # Created by
            created_by = bill.created_by or "System"
            self.bills_table.setItem(row, 7, QTableWidgetItem(created_by))

            # Actions - Create properly sized button
            actions_btn = self._create_table_button("View")
            actions_btn.clicked.connect(lambda checked, b_id=bill.id: self.view_bill(b_id))
            self.bills_table.setCellWidget(row, 8, actions_btn)

    def search_bills(self):
        """Search for bills"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_bills()
            return

        bills = PurchaseService.search(self.db, search_term)
        self.populate_table(bills)

    def apply_filters(self):
        """Apply filters based on status and date range"""
        status = self.status_combo.currentData()
        from_date = self.from_date.date().toPyDate()
        to_date = self.to_date.date().toPyDate()

        # Convert to datetime
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())

        all_bills = PurchaseService.get_by_date_range(self.db, from_datetime, to_datetime)

        # Filter by status
        if status == "pending":
            filtered_bills = [b for b in all_bills if not b.is_delivered]
        elif status == "delivered":
            filtered_bills = [b for b in all_bills if b.is_delivered]
        else:
            filtered_bills = all_bills

        self.populate_table(filtered_bills)

    def view_bill(self, bill_id: int):
        """View bill details"""
        bill = PurchaseService.get_by_id(self.db, bill_id)
        if bill:
            self.bill_selected.emit(bill_id)
            # Show detailed view in a dialog or new screen
            QMessageBox.information(
                self, "Bill Details",
                f"Bill: {bill.bill_number}\n"
                f"Farmer: {bill.farmer.name}\n"
                f"Net Weight: {float(bill.net_weight):,.2f} kg\n"
                f"Total Payment: RM {float(bill.total_payment):,.2f}"
            )

    # Edit functionality disabled per user request
    # This code can be re-enabled in the future if needed
    # def edit_bill(self):
    #     """Edit selected bill"""
    #     selected_rows = self.bills_table.selectedIndexes()
    #     if not selected_rows:
    #         QMessageBox.warning(self, "Warning", "Please select a bill to edit")
    #         return
    #
    #     bill_id = self.bills_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
    #     bill = PurchaseService.get_by_id(self.db, bill_id)
    #
    #     if not bill:
    #         QMessageBox.warning(self, "Warning", "Bill not found")
    #         return
    #
    #     if bill.is_delivered:
    #         QMessageBox.warning(self, "Warning", "Cannot edit delivered bills")
    #         return
    #
    #     # Open edit dialog
    #     dialog = PurchaseEditDialog(bill_id=bill_id, parent=self)
    #     if dialog.exec() == QDialog.Accepted:
    #         # Refresh the table to show updated data
    #         self.load_bills()
    #         QMessageBox.information(
    #             self, "Success",
    #             f"Bill {bill.bill_number} has been updated"
    #         )

    def print_receipt(self):
        """Print receipt for selected bill with option to export to PDF"""
        selected_rows = self.bills_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a bill to print")
            return

        bill_id = self.bills_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        bill = PurchaseService.get_by_id(self.db, bill_id)

        if not bill:
            QMessageBox.warning(self, "Warning", "Bill not found")
            return

        # Show receipt export dialog
        dialog = ReceiptExportDialog(
            receipt_type='purchase',
            receipt_number=bill.bill_number,
            parent=self
        )

        if dialog.exec() == QDialog.Accepted:
            try:
                action = dialog.get_action()
                pdf_path = dialog.get_pdf_path()

                # Get company info from config
                company_info = {
                    'name': ConfigService.get_value(self.db, 'company_name', 'AYOP BIN ARSHAD'),
                    'address_1': ConfigService.get_value(
                        self.db, 'company_address',
                        'LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR'
                    ),
                    'address_2': ConfigService.get_value(
                        self.db, 'company_address_2', 'SELANGOR DARUL EHSAN'
                    ),
                    'registration': ConfigService.get_value(self.db, 'company_registration', '474523-K'),
                    'phone': ConfigService.get_value(self.db, 'company_phone', '0162120051')
                }

                # Generate receipt text
                receipt = PurchaseReceiptFormatter.format_receipt(bill, company_info)

                # Handle print action
                if dialog.should_print():
                    print(receipt)
                    print("\n" + "="*80)
                    print("Receipt printed to console (printer integration pending)")
                    print("="*80 + "\n")

                # Handle PDF export
                output_pdf_path = None
                if dialog.should_export_pdf():
                    output_pdf_path = ReceiptPdfService.export_purchase_receipt_pdf(
                        db=self.db,
                        bill_id=bill_id,
                        output_path=pdf_path,
                        return_bytes=False
                    )

                # Show success message
                if action == 'print':
                    QMessageBox.information(
                        self, "Success",
                        "Receipt printed to console.\n\n"
                        "Note: Physical printer integration not yet implemented."
                    )
                elif action == 'pdf':
                    QMessageBox.information(
                        self, "Success",
                        f"Receipt exported to PDF successfully!\n\n"
                        f"Location: {output_pdf_path}"
                    )
                    # Optionally open the PDF
                    self._open_pdf_file(output_pdf_path)
                elif action == 'both':
                    QMessageBox.information(
                        self, "Success",
                        f"Receipt printed to console and exported to PDF!\n\n"
                        f"PDF Location: {output_pdf_path}\n\n"
                        f"Note: Physical printer integration not yet implemented."
                    )
                    # Optionally open the PDF
                    self._open_pdf_file(output_pdf_path)

            except ReceiptPdfError as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to process receipt:\n{str(e)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Unexpected error:\n{str(e)}"
                )

    def _open_pdf_file(self, file_path: str):
        """
        Optionally open PDF file with system default viewer

        Args:
            file_path: Path to PDF file
        """
        if not file_path or not os.path.exists(file_path):
            return

        reply = QMessageBox.question(
            self, "Open PDF",
            "Would you like to open the PDF file now?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                import platform
                import subprocess

                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', file_path])
                else:  # Linux
                    subprocess.run(['xdg-open', file_path])
            except Exception as e:
                QMessageBox.warning(
                    self, "Warning",
                    f"Could not open PDF file:\n{str(e)}\n\n"
                    f"Location: {file_path}"
                )

    def delete_bill(self):
        """Delete selected bill"""
        selected_rows = self.bills_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a bill to delete")
            return

        bill_id = self.bills_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        bill = PurchaseService.get_by_id(self.db, bill_id)

        if not bill:
            return

        if bill.is_delivered:
            QMessageBox.warning(self, "Warning", "Cannot delete delivered bills")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete bill {bill.bill_number}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if PurchaseService.delete(self.db, bill_id):
                QMessageBox.information(self, "Success", "Bill deleted successfully")
                self.load_bills()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete bill")

    def refresh(self):
        """Refresh the bills list"""
        self.load_bills()
