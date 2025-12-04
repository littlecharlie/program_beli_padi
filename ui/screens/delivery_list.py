"""
Delivery Invoice List Screen
View and manage delivery invoices
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QDateEdit, QComboBox, QAbstractItemView, QDialog
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime
from config.database import get_db
from services.delivery_service import DeliveryService
from services.purchase_service import PurchaseService
from printing.delivery_receipt import DeliveryReceiptFormatter
from services.config_service import ConfigService
from services.receipt_pdf_service import ReceiptPdfService, ReceiptPdfError
from ui.dialogs.receipt_export_dialog import ReceiptExportDialog
import os


class DeliveryListScreen(QWidget):
    """Screen for viewing and managing delivery invoices"""

    # Signals
    invoice_selected = pyqtSignal(int)  # invoice_id
    create_delivery_invoice = pyqtSignal()  # Signal to create new delivery invoice

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.setup_ui()
        self.load_invoices()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title and Add Button Row
        title_layout = QHBoxLayout()
        title = QLabel("Delivery Invoices")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        # Add New Button
        add_new_btn = QPushButton("+ Create New Delivery Invoice")
        add_new_btn.setStyleSheet("""
            background-color: #4caf50;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 600;
        """)
        add_new_btn.clicked.connect(self.create_delivery_invoice.emit)
        title_layout.addWidget(add_new_btn)

        main_layout.addLayout(title_layout)

        # Search/Filter Group
        search_layout = self._create_search_group()
        main_layout.addLayout(search_layout)

        # Invoices Table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(7)
        self.invoices_table.setHorizontalHeaderLabels([
            "Invoice No",
            "Date",
            "Rice Mill",
            "Truck",
            "Bills",
            "Total Weight",
            "Actions"
        ])
        self.invoices_table.setColumnWidth(0, 100)
        self.invoices_table.setColumnWidth(1, 130)
        self.invoices_table.setColumnWidth(2, 150)
        self.invoices_table.setColumnWidth(3, 100)
        self.invoices_table.setColumnWidth(4, 70)
        self.invoices_table.setColumnWidth(5, 120)
        self.invoices_table.setColumnWidth(6, 100)
        self.invoices_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self.invoices_table.setSelectionMode(
            QTableWidget.SingleSelection
        )
        # Disable cell editing - users must use the Edit button
        self.invoices_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        main_layout.addWidget(self.invoices_table)

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

        # Search by invoice number
        layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Invoice number")
        self.search_input.returnPressed.connect(self.search_invoices)
        layout.addWidget(self.search_input)

        # Filter by mill
        layout.addWidget(QLabel("Mill:"))
        self.mill_combo = QComboBox()
        self.mill_combo.addItem("All Mills", None)
        self.load_mills()
        self.mill_combo.currentIndexChanged.connect(self.apply_filters)
        layout.addWidget(self.mill_combo)

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
        search_btn.clicked.connect(self.search_invoices)
        layout.addWidget(search_btn)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_invoices)
        layout.addWidget(refresh_btn)

        layout.addStretch()

        return layout

    def _create_stats_group(self) -> QHBoxLayout:
        """Create statistics group"""
        layout = QHBoxLayout()

        stats = DeliveryService.get_statistics(self.db)

        layout.addWidget(QLabel(f"Total Invoices: {stats['total_invoices']}"))
        layout.addWidget(QLabel(f"Total Bills Delivered: {stats['total_bills_delivered']}"))
        layout.addWidget(QLabel(f"Total Weight: {stats['total_weight']:,.2f} kg"))
        layout.addWidget(QLabel(f"Avg Weight per Invoice: {stats['avg_invoice_weight']:,.2f} kg"))
        layout.addStretch()

        return layout

    def _create_button_group(self) -> QHBoxLayout:
        """Create button group"""
        layout = QHBoxLayout()

        self.view_btn = QPushButton("View Bills")
        self.view_btn.clicked.connect(self.view_invoice)

        self.print_btn = QPushButton("Print Receipt")
        self.print_btn.clicked.connect(self.print_receipt)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self.delete_btn.clicked.connect(self.delete_invoice)

        layout.addWidget(self.view_btn)
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

    def load_mills(self):
        """Load rice mills into combo box"""
        from services.rice_mill_service import RiceMillService
        mills = RiceMillService.get_all(self.db, active_only=True)
        for mill in mills:
            self.mill_combo.addItem(mill.mill_name, mill.id)

    def load_invoices(self):
        """Load all invoices into table"""
        invoices = DeliveryService.get_all(self.db)
        self.populate_table(invoices)

    def populate_table(self, invoices):
        """Populate table with invoices"""
        self.invoices_table.setRowCount(len(invoices))

        for row, invoice in enumerate(invoices):
            # Set row height for consistent button sizing
            self.invoices_table.setRowHeight(row, 44)

            # Invoice number
            item = QTableWidgetItem(invoice.invoice_number)
            item.setData(Qt.UserRole, invoice.id)
            self.invoices_table.setItem(row, 0, item)

            # Date
            date_str = invoice.invoice_date.strftime("%d/%m/%Y %H:%M")
            self.invoices_table.setItem(row, 1, QTableWidgetItem(date_str))

            # Rice mill
            mill_name = invoice.mill.mill_name if invoice.mill else "Unknown"
            self.invoices_table.setItem(row, 2, QTableWidgetItem(mill_name))

            # Truck
            truck_number = invoice.truck.truck_number if invoice.truck else "Unknown"
            self.invoices_table.setItem(row, 3, QTableWidgetItem(truck_number))

            # Bills count
            items = DeliveryService.get_items(self.db, invoice.id)
            self.invoices_table.setItem(row, 4, QTableWidgetItem(str(len(items))))

            # Total weight
            weight_str = f"{float(invoice.total_weight):,.2f} kg"
            self.invoices_table.setItem(row, 5, QTableWidgetItem(weight_str))

            # Actions - Create properly sized button
            actions_btn = self._create_table_button("View")
            actions_btn.clicked.connect(lambda checked, inv_id=invoice.id: self.view_invoice(inv_id))
            self.invoices_table.setCellWidget(row, 6, actions_btn)

    def search_invoices(self):
        """Search for invoices"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_invoices()
            return

        invoices = DeliveryService.search(self.db, search_term)
        self.populate_table(invoices)

    def apply_filters(self):
        """Apply filters"""
        mill_id = self.mill_combo.currentData()
        from_date = self.from_date.date().toPyDate()
        to_date = self.to_date.date().toPyDate()

        from datetime import datetime
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())

        all_invoices = DeliveryService.get_by_date_range(self.db, from_datetime, to_datetime)

        # Filter by mill
        if mill_id:
            filtered_invoices = [inv for inv in all_invoices if inv.mill_id == mill_id]
        else:
            filtered_invoices = all_invoices

        self.populate_table(filtered_invoices)

    def view_invoice(self, invoice_id: int = None):
        """View invoice details"""
        if invoice_id is None:
            selected_rows = self.invoices_table.selectedIndexes()
            if not selected_rows:
                QMessageBox.warning(self, "Warning", "Please select an invoice")
                return
            invoice_id = self.invoices_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)

        invoice = DeliveryService.get_by_id(self.db, invoice_id)
        if invoice:
            bills = DeliveryService.get_bills_for_invoice(self.db, invoice_id)
            bill_count = len(bills)
            total_weight = sum(float(b.net_weight) for b in bills)
            total_payment = sum(float(b.total_payment) for b in bills)

            bill_list = "\n".join([f"  {b.bill_number} - {b.farmer.name if b.farmer else 'Unknown'}" for b in bills[:5]])
            if len(bills) > 5:
                bill_list += f"\n  ... and {len(bills) - 5} more"

            self.invoice_selected.emit(invoice_id)
            QMessageBox.information(
                self, "Invoice Details",
                f"Invoice: {invoice.invoice_number}\n"
                f"Date: {invoice.invoice_date.strftime('%d/%m/%Y %H:%M')}\n"
                f"Mill: {invoice.mill.mill_name if invoice.mill else 'Unknown'}\n"
                f"Truck: {invoice.truck.truck_number if invoice.truck else 'Unknown'}\n"
                f"Bills: {bill_count}\n"
                f"Total Weight: {total_weight:,.2f} kg\n"
                f"Total Payment: RM {total_payment:,.2f}\n\n"
                f"Bills:\n{bill_list}"
            )

    def print_receipt(self):
        """Print receipt for selected invoice with option to export to PDF"""
        selected_rows = self.invoices_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an invoice")
            return

        invoice_id = self.invoices_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        invoice = DeliveryService.get_by_id(self.db, invoice_id)

        if not invoice:
            QMessageBox.warning(self, "Warning", "Invoice not found")
            return

        # Show receipt export dialog
        dialog = ReceiptExportDialog(
            receipt_type='delivery',
            receipt_number=invoice.invoice_number,
            parent=self
        )

        if dialog.exec() == QDialog.Accepted:
            try:
                action = dialog.get_action()
                pdf_path = dialog.get_pdf_path()

                # Get company info
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

                # Generate receipt text - NOW PASSING DATABASE SESSION
                receipt = DeliveryReceiptFormatter.format_receipt(self.db, invoice, company_info)

                # Handle print action
                if dialog.should_print():
                    print(receipt)
                    print("\n" + "="*80)
                    print("Receipt printed to console (printer integration pending)")
                    print("="*80 + "\n")

                # Handle PDF export
                output_pdf_path = None
                if dialog.should_export_pdf():
                    output_pdf_path = ReceiptPdfService.export_delivery_receipt_pdf(
                        db=self.db,
                        invoice_id=invoice_id,
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

    def delete_invoice(self):
        """Delete selected invoice"""
        selected_rows = self.invoices_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select an invoice")
            return

        invoice_id = self.invoices_table.item(selected_rows[0].row(), 0).data(Qt.UserRole)
        invoice = DeliveryService.get_by_id(self.db, invoice_id)

        if not invoice:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete invoice {invoice.invoice_number}?\n"
            f"Associated bills will be marked as undelivered.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if DeliveryService.delete(self.db, invoice_id):
                QMessageBox.information(self, "Success", "Invoice deleted successfully")
                self.load_invoices()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete invoice")

    def refresh(self):
        """Refresh the invoices list"""
        self.load_invoices()
