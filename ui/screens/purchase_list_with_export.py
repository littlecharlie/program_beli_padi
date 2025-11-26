"""
Purchase Bill List Screen with PDF Export Integration
Enhanced version with PDF export capabilities
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QDateEdit, QComboBox, QSpinBox, QToolBar
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime, timedelta
from config.database import get_db
from services.purchase_service import PurchaseService
from printing.purchase_receipt import PurchaseReceiptFormatter
from services.config_service import ConfigService

# PDF Export imports
from ui.dialogs.pdf_export_dialog import PdfExportDialog, BatchExportProgressDialog, QuickPdfExportDialog
from ui.widgets.export_helpers import (
    ExportNotification, FileOperations, generate_export_filename
)
from ui.widgets.context_menu_mixin import TableContextMenuMixin


class PurchaseListScreenWithExport(QWidget, TableContextMenuMixin):
    """Screen for viewing and managing purchase bills with PDF export"""

    # Signals
    bill_selected = pyqtSignal(int)  # bill_id
    create_purchase_bill = pyqtSignal()  # Signal to create new purchase bill

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.current_bills = []  # Store current filtered bills
        self.setup_ui()
        self.load_bills()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title and Export Toolbar
        title_layout = QHBoxLayout()
        title = QLabel("Purchase Bills")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        # Export toolbar buttons
        export_btn = QPushButton("Export Selected to PDF")
        export_btn.setProperty("success", True)
        export_btn.setToolTip("Export selected bills to PDF (Right-click for more options)")
        export_btn.clicked.connect(self._export_selected)
        title_layout.addWidget(export_btn)

        export_all_btn = QPushButton("Export All to PDF")
        export_all_btn.setProperty("secondary", True)
        export_all_btn.setToolTip("Export all bills to PDF")
        export_all_btn.clicked.connect(self._export_all)
        title_layout.addWidget(export_all_btn)

        main_layout.addLayout(title_layout)

        # Search/Filter Group
        search_layout = self._create_search_group()
        main_layout.addLayout(search_layout)

        # Bills Table with Context Menu
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

        # Setup context menu from mixin
        self.setup_table_context_menu(self.bills_table, export_enabled=True)

        # Connect signals from mixin
        self.export_single_pdf.connect(self._export_single_bill)
        self.export_batch_pdf.connect(self._export_batch_bills)
        self.view_details.connect(self.view_bill)
        self.edit_item.connect(self.edit_bill)
        self.delete_item.connect(lambda bill_id: self.delete_bill(bill_id))
        self.print_receipt.connect(self._print_bill_receipt)

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

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(lambda: self.edit_bill(self._get_selected_bill_id()))

        self.print_btn = QPushButton("Print Receipt")
        self.print_btn.clicked.connect(lambda: self._print_bill_receipt(self._get_selected_bill_id()))

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self.delete_btn.clicked.connect(lambda: self.delete_bill(self._get_selected_bill_id()))

        layout.addWidget(self.new_bill_btn)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.print_btn)
        layout.addWidget(self.delete_btn)
        layout.addStretch()

        return layout

    def _on_create_purchase_bill(self):
        """Handle create new purchase bill button click"""
        self.create_purchase_bill.emit()

    def load_bills(self):
        """Load all bills into table"""
        bills = PurchaseService.get_all(self.db)
        self.current_bills = bills
        self.populate_table(bills)

    def populate_table(self, bills):
        """Populate table with bills"""
        self.bills_table.setRowCount(len(bills))

        for row, bill in enumerate(bills):
            # Bill number
            item = QTableWidgetItem(bill.bill_number)
            item.setData(Qt.ItemDataRole.UserRole, bill.id)
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

            # Actions
            actions_btn = QPushButton("View")
            actions_btn.clicked.connect(lambda checked, b_id=bill.id: self.view_bill(b_id))
            self.bills_table.setCellWidget(row, 8, actions_btn)

    def search_bills(self):
        """Search for bills"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_bills()
            return

        bills = PurchaseService.search(self.db, search_term)
        self.current_bills = bills
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

        self.current_bills = filtered_bills
        self.populate_table(filtered_bills)

    def view_bill(self, bill_id: int):
        """View bill details"""
        if not bill_id:
            return
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

    def edit_bill(self, bill_id: int):
        """Edit selected bill"""
        if not bill_id:
            QMessageBox.warning(self, "Warning", "Please select a bill to edit")
            return

        bill = PurchaseService.get_by_id(self.db, bill_id)

        if bill and bill.is_delivered:
            QMessageBox.warning(self, "Warning", "Cannot edit delivered bills")
            return

        QMessageBox.information(self, "Info", "Edit functionality not yet implemented")

    def _print_bill_receipt(self, bill_id: int):
        """Print receipt for bill"""
        if not bill_id:
            QMessageBox.warning(self, "Warning", "Please select a bill to print")
            return

        bill = PurchaseService.get_by_id(self.db, bill_id)

        if bill:
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

            receipt = PurchaseReceiptFormatter.format_receipt(bill, company_info)
            print(receipt)
            QMessageBox.information(self, "Info", "Receipt printed to console. Printer integration not yet implemented.")

    def delete_bill(self, bill_id: int = None):
        """Delete bill"""
        if not bill_id:
            QMessageBox.warning(self, "Warning", "Please select a bill to delete")
            return

        bill = PurchaseService.get_by_id(self.db, bill_id)

        if not bill:
            return

        if bill.is_delivered:
            QMessageBox.warning(self, "Warning", "Cannot delete delivered bills")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete bill {bill.bill_number}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if PurchaseService.delete(self.db, bill_id):
                QMessageBox.information(self, "Success", "Bill deleted successfully")
                self.load_bills()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete bill")

    # ========== PDF Export Methods ==========

    def _export_selected(self):
        """Export selected bills to PDF"""
        selected_rows = self.bills_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one bill to export")
            return

        bill_ids = []
        for row in selected_rows:
            item = self.bills_table.item(row.row(), 0)
            if item:
                bill_id = item.data(Qt.ItemDataRole.UserRole)
                if bill_id:
                    bill_ids.append(bill_id)

        if len(bill_ids) == 1:
            self._export_single_bill(bill_ids[0])
        else:
            self._export_batch_bills(bill_ids)

    def _export_all(self):
        """Export all current bills to PDF"""
        if not self.current_bills:
            QMessageBox.warning(self, "No Bills", "No bills to export")
            return

        bill_ids = [bill.id for bill in self.current_bills]
        self._export_batch_bills(bill_ids)

    def _export_single_bill(self, bill_id: int):
        """Export single bill to PDF"""
        bill = PurchaseService.get_by_id(self.db, bill_id)
        if not bill:
            QMessageBox.warning(self, "Error", "Bill not found")
            return

        # Generate default filename
        filename = generate_export_filename("purchase", bill.bill_number, timestamp=True)

        # Show quick export dialog
        dialog = QuickPdfExportDialog("purchase", filename, self)
        if dialog.exec():
            config = dialog.get_export_config()
            self._perform_single_export(bill, config)

    def _export_batch_bills(self, bill_ids: list):
        """Export multiple bills to PDF"""
        if not bill_ids:
            return

        # Generate default filename
        filename = generate_export_filename("purchase", f"{len(bill_ids)}_bills", timestamp=True)

        # Show full export dialog
        dialog = PdfExportDialog("purchase", len(bill_ids), filename, self)
        if dialog.exec():
            config = dialog.get_export_config()
            self._perform_batch_export(bill_ids, config)

    def _perform_single_export(self, bill, config: dict):
        """Perform actual single PDF export"""
        try:
            # TODO: Implement actual PDF generation using ReportLab or similar
            # This is a placeholder showing the structure

            file_path = config['file_path']

            # Simulate PDF generation
            # In real implementation, use PdfGenerator class
            success = self._generate_purchase_bill_pdf(bill, file_path, config)

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

    def _perform_batch_export(self, bill_ids: list, config: dict):
        """Perform batch PDF export with progress dialog"""
        # Show progress dialog
        progress = BatchExportProgressDialog(len(bill_ids), self)
        progress.show()

        try:
            file_path = config['file_path']
            bills = [PurchaseService.get_by_id(self.db, bill_id) for bill_id in bill_ids]
            bills = [b for b in bills if b]  # Filter out None

            # Simulate batch export with progress
            for idx, bill in enumerate(bills, 1):
                progress.update_progress(idx, bill.bill_number)

                # TODO: Generate PDF for each bill
                # In real implementation, append to single PDF

                if progress.result() == QMessageBox.StandardButton.Cancel:
                    ExportNotification.show_info(self, "Export Cancelled", "Export was cancelled by user")
                    return

            progress.set_completed()
            progress.accept()

            ExportNotification.show_success(self, file_path, len(bills))

            # Post-export actions
            if config.get('open_file'):
                FileOperations.open_file(file_path)
            if config.get('open_folder'):
                FileOperations.open_folder(file_path)

        except Exception as e:
            progress.reject()
            ExportNotification.show_error(self, str(e))

    def _generate_purchase_bill_pdf(self, bill, file_path: str, config: dict) -> bool:
        """
        Generate PDF for purchase bill
        TODO: Implement using ReportLab or similar PDF library

        Args:
            bill: PurchaseBill object
            file_path: Output file path
            config: Export configuration dict

        Returns:
            True if successful, False otherwise
        """
        # This is a placeholder - implement actual PDF generation
        print(f"Generating PDF for bill {bill.bill_number} to {file_path}")
        print(f"Config: {config}")

        # Simulate file creation
        from pathlib import Path
        Path(file_path).touch()

        return True

    def _get_selected_bill_id(self) -> int:
        """Get selected bill ID from table"""
        selected_rows = self.bills_table.selectedIndexes()
        if not selected_rows:
            return None

        item = self.bills_table.item(selected_rows[0].row(), 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def refresh(self):
        """Refresh the bills list"""
        self.load_bills()
