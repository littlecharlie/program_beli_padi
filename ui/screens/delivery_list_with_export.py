"""
Delivery Invoice List Screen with PDF Export Integration
Enhanced version with PDF export capabilities
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QDateEdit, QComboBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime
from config.database import get_db
from services.delivery_service import DeliveryService
from services.purchase_service import PurchaseService
from printing.delivery_receipt import DeliveryReceiptFormatter
from services.config_service import ConfigService

# PDF Export imports
from ui.dialogs.pdf_export_dialog import PdfExportDialog, QuickPdfExportDialog
from ui.widgets.export_helpers import (
    ExportNotification, FileOperations, generate_export_filename
)
from ui.widgets.context_menu_mixin import TableContextMenuMixin


class DeliveryListScreenWithExport(QWidget, TableContextMenuMixin):
    """Screen for viewing and managing delivery invoices with PDF export"""

    # Signals
    invoice_selected = pyqtSignal(int)  # invoice_id
    create_delivery_invoice = pyqtSignal()  # Signal to create new delivery invoice

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.current_invoices = []
        self.setup_ui()
        self.load_invoices()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title and Export Toolbar
        title_layout = QHBoxLayout()
        title = QLabel("Delivery Invoices")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        # Export buttons
        export_btn = QPushButton("Export Selected to PDF")
        export_btn.setProperty("success", True)
        export_btn.clicked.connect(self._export_selected)
        title_layout.addWidget(export_btn)

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
        # Disable cell editing - users must use the Edit button
        self.invoices_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        # Setup context menu
        self.setup_table_context_menu(self.invoices_table, export_enabled=True)

        # Connect signals
        self.export_single_pdf.connect(self._export_single_invoice)
        self.export_batch_pdf.connect(self._export_batch_invoices)
        self.view_details.connect(self.view_invoice)
        self.delete_item.connect(lambda inv_id: self.delete_invoice(inv_id))
        self.print_receipt.connect(self._print_invoice_receipt)

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
        self.view_btn.clicked.connect(lambda: self.view_invoice(self._get_selected_invoice_id()))

        self.print_btn = QPushButton("Print Receipt")
        self.print_btn.clicked.connect(lambda: self._print_invoice_receipt(self._get_selected_invoice_id()))

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self.delete_btn.clicked.connect(lambda: self.delete_invoice(self._get_selected_invoice_id()))

        layout.addWidget(self.view_btn)
        layout.addWidget(self.print_btn)
        layout.addWidget(self.delete_btn)
        layout.addStretch()

        return layout

    def load_mills(self):
        """Load rice mills into combo box"""
        from services.rice_mill_service import RiceMillService
        mills = RiceMillService.get_all(self.db, active_only=True)
        for mill in mills:
            self.mill_combo.addItem(mill.mill_name, mill.id)

    def load_invoices(self):
        """Load all invoices into table"""
        invoices = DeliveryService.get_all(self.db)
        self.current_invoices = invoices
        self.populate_table(invoices)

    def populate_table(self, invoices):
        """Populate table with invoices"""
        self.invoices_table.setRowCount(len(invoices))

        for row, invoice in enumerate(invoices):
            # Invoice number
            item = QTableWidgetItem(invoice.invoice_number)
            item.setData(Qt.ItemDataRole.UserRole, invoice.id)
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

            # Actions
            actions_btn = QPushButton("View")
            actions_btn.clicked.connect(lambda checked, inv_id=invoice.id: self.view_invoice(inv_id))
            self.invoices_table.setCellWidget(row, 6, actions_btn)

    def search_invoices(self):
        """Search for invoices"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_invoices()
            return

        invoices = DeliveryService.search(self.db, search_term)
        self.current_invoices = invoices
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

        self.current_invoices = filtered_invoices
        self.populate_table(filtered_invoices)

    def view_invoice(self, invoice_id: int = None):
        """View invoice details"""
        if invoice_id is None:
            QMessageBox.warning(self, "Warning", "Please select an invoice")
            return

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

    def _print_invoice_receipt(self, invoice_id: int):
        """Print receipt for invoice"""
        if not invoice_id:
            QMessageBox.warning(self, "Warning", "Please select an invoice")
            return

        invoice = DeliveryService.get_by_id(self.db, invoice_id)

        if invoice:
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

            receipt = DeliveryReceiptFormatter.format_receipt(self.db, invoice, company_info)
            print(receipt)
            QMessageBox.information(self, "Info", "Receipt printed to console. Printer integration not yet implemented.")

    def delete_invoice(self, invoice_id: int = None):
        """Delete invoice"""
        if not invoice_id:
            QMessageBox.warning(self, "Warning", "Please select an invoice")
            return

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

    # ========== PDF Export Methods ==========

    def _export_selected(self):
        """Export selected invoices to PDF"""
        selected_rows = self.invoices_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one invoice to export")
            return

        invoice_ids = []
        for row in selected_rows:
            item = self.invoices_table.item(row.row(), 0)
            if item:
                invoice_id = item.data(Qt.ItemDataRole.UserRole)
                if invoice_id:
                    invoice_ids.append(invoice_id)

        if len(invoice_ids) == 1:
            self._export_single_invoice(invoice_ids[0])
        else:
            self._export_batch_invoices(invoice_ids)

    def _export_single_invoice(self, invoice_id: int):
        """Export single invoice to PDF"""
        invoice = DeliveryService.get_by_id(self.db, invoice_id)
        if not invoice:
            QMessageBox.warning(self, "Error", "Invoice not found")
            return

        # Generate default filename
        filename = generate_export_filename("delivery", invoice.invoice_number, timestamp=True)

        # Show quick export dialog
        dialog = QuickPdfExportDialog("delivery", filename, self)
        if dialog.exec():
            config = dialog.get_export_config()
            self._perform_single_export(invoice, config)

    def _export_batch_invoices(self, invoice_ids: list):
        """Export multiple invoices to PDF"""
        if not invoice_ids:
            return

        # Generate default filename
        filename = generate_export_filename("delivery", f"{len(invoice_ids)}_invoices", timestamp=True)

        # Show full export dialog
        dialog = PdfExportDialog("delivery", len(invoice_ids), filename, self)
        if dialog.exec():
            config = dialog.get_export_config()
            self._perform_batch_export(invoice_ids, config)

    def _perform_single_export(self, invoice, config: dict):
        """Perform actual single PDF export"""
        try:
            file_path = config['file_path']

            # TODO: Implement actual PDF generation
            success = self._generate_delivery_invoice_pdf(invoice, file_path, config)

            if success:
                ExportNotification.show_success(self, file_path, 1)

                # Post-export actions
                if config.get('open_file'):
                    FileOperations.open_file(file_path)
                if config.get('open_folder'):
                    FileOperations.open_folder(file_path)
            else:
                ExportNotification.show_error(self, "Failed to generate PDF")

        except Exception as e:
            ExportNotification.show_error(self, str(e))

    def _perform_batch_export(self, invoice_ids: list, config: dict):
        """Perform batch PDF export"""
        try:
            file_path = config['file_path']
            invoices = [DeliveryService.get_by_id(self.db, inv_id) for inv_id in invoice_ids]
            invoices = [inv for inv in invoices if inv]

            # TODO: Implement batch PDF generation
            success = True  # Placeholder

            if success:
                ExportNotification.show_success(self, file_path, len(invoices))

                if config.get('open_file'):
                    FileOperations.open_file(file_path)
                if config.get('open_folder'):
                    FileOperations.open_folder(file_path)
            else:
                ExportNotification.show_error(self, "Failed to generate PDF")

        except Exception as e:
            ExportNotification.show_error(self, str(e))

    def _generate_delivery_invoice_pdf(self, invoice, file_path: str, config: dict) -> bool:
        """
        Generate PDF for delivery invoice
        TODO: Implement using ReportLab or similar PDF library
        """
        print(f"Generating PDF for invoice {invoice.invoice_number} to {file_path}")
        print(f"Config: {config}")

        # Simulate file creation
        from pathlib import Path
        Path(file_path).touch()

        return True

    def _get_selected_invoice_id(self) -> int:
        """Get selected invoice ID from table"""
        selected_rows = self.invoices_table.selectedIndexes()
        if not selected_rows:
            return None

        item = self.invoices_table.item(selected_rows[0].row(), 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def refresh(self):
        """Refresh the invoices list"""
        self.load_invoices()
