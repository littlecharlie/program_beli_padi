"""
Delivery Invoice Entry Screen
UI for creating delivery invoices from purchase bills
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget,
    QTableWidgetItem, QFormLayout, QScrollArea, QCheckBox,
    QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from decimal import Decimal
from config.database import get_db
from services.purchase_service import PurchaseService
from services.delivery_service import DeliveryService
from services.rice_mill_service import RiceMillService
from services.truck_service import TruckService


class DeliveryEntryScreen(QWidget):
    """Screen for creating delivery invoices"""

    # Signal when invoice is created
    invoice_created = pyqtSignal(int)  # invoice_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.selected_mill_id = None
        self.selected_truck_id = None
        self.selected_bill_ids = []
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Create Delivery Invoice")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Delivery Information Group
        delivery_info = self._create_delivery_info_group()
        scroll_layout.addWidget(delivery_info)

        # Available Bills Group
        bills_group = self._create_bills_group()
        scroll_layout.addWidget(bills_group)

        # Summary Group
        summary_group = self._create_summary_group()
        scroll_layout.addWidget(summary_group)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Button Group
        button_layout = self._create_button_group()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_delivery_info_group(self) -> QGroupBox:
        """Create delivery information group"""
        group = QGroupBox("Delivery Information")
        layout = QFormLayout()

        # Invoice number (auto)
        self.invoice_number_input = QLineEdit()
        self.invoice_number_input.setReadOnly(True)
        self.invoice_number_input.setText("(Auto-generated)")
        layout.addRow("Invoice Number:", self.invoice_number_input)

        # Date
        self.invoice_date_input = QLineEdit()
        self.invoice_date_input.setReadOnly(True)
        self.invoice_date_input.setText(datetime.now().strftime("%d/%m/%Y %H:%M"))
        layout.addRow("Date/Time:", self.invoice_date_input)

        # Rice Mill
        layout.addRow(QLabel("Rice Mill:"))
        mill_layout = QHBoxLayout()
        self.mill_combo = QComboBox()
        self.load_mills()
        self.mill_combo.currentIndexChanged.connect(self.on_mill_changed)
        mill_layout.addWidget(self.mill_combo)
        mill_layout.addStretch()
        layout.addRow(mill_layout)

        # Truck
        layout.addRow(QLabel("Truck:"))
        truck_layout = QHBoxLayout()
        self.truck_combo = QComboBox()
        self.load_trucks()
        self.truck_combo.currentIndexChanged.connect(self.on_truck_changed)
        truck_layout.addWidget(self.truck_combo)
        truck_layout.addStretch()
        layout.addRow(truck_layout)

        group.setLayout(layout)
        return group

    def _create_bills_group(self) -> QGroupBox:
        """Create available bills group"""
        group = QGroupBox("Available Purchase Bills (Not Yet Delivered)")
        layout = QVBoxLayout()

        # Buttons
        btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_bills)
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all_bills)
        self.filter_mill_btn = QPushButton("Filter by Current Mill")
        self.filter_mill_btn.clicked.connect(self.filter_by_mill)
        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.deselect_all_btn)
        btn_layout.addWidget(self.filter_mill_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Bills table
        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(6)
        self.bills_table.setHorizontalHeaderLabels([
            "Select",
            "Bill No",
            "Date",
            "Farmer Name",
            "Net Weight (kg)",
            "Total Payment"
        ])
        self.bills_table.setColumnWidth(0, 60)
        self.bills_table.setColumnWidth(1, 80)
        self.bills_table.setColumnWidth(2, 120)
        self.bills_table.setColumnWidth(3, 150)
        self.bills_table.setColumnWidth(4, 120)
        self.bills_table.setColumnWidth(5, 120)

        self.bills_table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.bills_table)

        # Load bills
        self.load_undelivered_bills()

        group.setLayout(layout)
        return group

    def _create_summary_group(self) -> QGroupBox:
        """Create summary group"""
        group = QGroupBox("Summary")
        layout = QFormLayout()

        self.selected_count_input = QLineEdit()
        self.selected_count_input.setReadOnly(True)
        layout.addRow("Bills Selected:", self.selected_count_input)

        self.total_weight_input = QLineEdit()
        self.total_weight_input.setReadOnly(True)
        layout.addRow("Total Weight:", self.total_weight_input)

        self.total_payment_input = QLineEdit()
        self.total_payment_input.setReadOnly(True)
        layout.addRow("Total Payment:", self.total_payment_input)

        group.setLayout(layout)
        return group

    def _create_button_group(self) -> QHBoxLayout:
        """Create button group"""
        layout = QHBoxLayout()

        self.create_btn = QPushButton("Create & Print")
        self.create_btn.setStyleSheet("background-color: #28a745; color: white;")
        self.create_btn.clicked.connect(self.create_invoice)

        self.create_only_btn = QPushButton("Create Only")
        self.create_only_btn.setStyleSheet("background-color: #007ACC; color: white;")
        self.create_only_btn.clicked.connect(self.create_only)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #6c757d; color: white;")
        self.cancel_btn.clicked.connect(self.cancel)

        layout.addWidget(self.create_btn)
        layout.addWidget(self.create_only_btn)
        layout.addStretch()
        layout.addWidget(self.cancel_btn)

        return layout

    def load_mills(self):
        """Load rice mills into combo box"""
        self.mill_combo.blockSignals(True)
        self.mill_combo.clear()

        mills = RiceMillService.get_all(self.db, active_only=True)
        for mill in mills:
            self.mill_combo.addItem(mill.mill_name, mill.id)

        self.mill_combo.blockSignals(False)

    def load_trucks(self):
        """Load trucks into combo box"""
        self.truck_combo.blockSignals(True)
        self.truck_combo.clear()

        trucks = TruckService.get_all(self.db, active_only=True)
        for truck in trucks:
            self.truck_combo.addItem(truck.truck_number, truck.id)

        self.truck_combo.blockSignals(False)

    def load_undelivered_bills(self):
        """Load undelivered bills into table"""
        bills = PurchaseService.get_undelivered(self.db)
        self.populate_bills_table(bills)

    def populate_bills_table(self, bills):
        """Populate bills table"""
        self.bills_table.setRowCount(len(bills))

        for row, bill in enumerate(bills):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.on_bill_selection_changed)
            self.bills_table.setCellWidget(row, 0, checkbox)

            # Bill number
            bill_item = QTableWidgetItem(bill.bill_number)
            bill_item.setData(Qt.ItemDataRole.UserRole, bill.id)
            self.bills_table.setItem(row, 1, bill_item)

            # Date
            date_str = bill.bill_date.strftime("%d/%m/%Y %H:%M")
            self.bills_table.setItem(row, 2, QTableWidgetItem(date_str))

            # Farmer name
            farmer_name = bill.farmer.name if bill.farmer else "Unknown"
            self.bills_table.setItem(row, 3, QTableWidgetItem(farmer_name))

            # Net weight
            weight_str = f"{float(bill.net_weight):,.2f}"
            self.bills_table.setItem(row, 4, QTableWidgetItem(weight_str))

            # Total payment
            payment_str = f"RM {float(bill.total_payment):,.2f}"
            self.bills_table.setItem(row, 5, QTableWidgetItem(payment_str))

    def on_mill_changed(self):
        """Handle mill selection change"""
        self.selected_mill_id = self.mill_combo.currentData()

    def on_truck_changed(self):
        """Handle truck selection change"""
        self.selected_truck_id = self.truck_combo.currentData()

    def on_bill_selection_changed(self):
        """Handle bill selection change"""
        self.update_summary()

    def select_all_bills(self):
        """Select all bills"""
        for row in range(self.bills_table.rowCount()):
            checkbox = self.bills_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)
        self.update_summary()

    def deselect_all_bills(self):
        """Deselect all bills"""
        for row in range(self.bills_table.rowCount()):
            checkbox = self.bills_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_summary()

    def filter_by_mill(self):
        """Filter bills by current mill selection"""
        if not self.selected_mill_id:
            QMessageBox.warning(self, "Warning", "Please select a mill first")
            return

        mill = RiceMillService.get_by_id(self.db, self.selected_mill_id)
        QMessageBox.information(
            self, "Info",
            f"Filtering by mill: {mill.mill_name}\n"
            "Note: Full implementation will filter bills by mill destination"
        )

    def get_selected_bills(self) -> list:
        """Get selected bill IDs"""
        selected_ids = []
        for row in range(self.bills_table.rowCount()):
            checkbox = self.bills_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                bill_item = self.bills_table.item(row, 1)
                bill_id = bill_item.data(Qt.ItemDataRole.UserRole)
                selected_ids.append(bill_id)
        return selected_ids

    def update_summary(self):
        """Update summary information"""
        selected_ids = self.get_selected_bills()

        if not selected_ids:
            self.selected_count_input.setText("0")
            self.total_weight_input.setText("0.00 kg")
            self.total_payment_input.setText("RM 0.00")
            return

        # Get bills
        bills = [PurchaseService.get_by_id(self.db, bid) for bid in selected_ids]
        bills = [b for b in bills if b]

        # Calculate totals
        total_weight = sum(float(b.net_weight) for b in bills)
        total_payment = sum(float(b.total_payment) for b in bills)

        self.selected_count_input.setText(str(len(bills)))
        self.total_weight_input.setText(f"{total_weight:,.2f} kg")
        self.total_payment_input.setText(f"RM {total_payment:,.2f}")

    def validate_inputs(self) -> tuple[bool, str]:
        """Validate inputs"""
        if not self.selected_mill_id:
            return False, "Please select a rice mill"

        if not self.selected_truck_id:
            return False, "Please select a truck"

        selected_ids = self.get_selected_bills()
        if not selected_ids:
            return False, "Please select at least one bill"

        return True, ""

    def create_invoice(self):
        """Create invoice and print"""
        invoice_id = self.create_delivery_invoice()
        if invoice_id:
            QMessageBox.information(self, "Info", "Invoice created. Printing not yet implemented.")

    def create_only(self):
        """Create invoice only"""
        self.create_delivery_invoice()

    def create_delivery_invoice(self) -> int:
        """Create delivery invoice"""
        is_valid, error = self.validate_inputs()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error)
            return None

        try:
            selected_ids = self.get_selected_bills()
            invoice = DeliveryService.create(
                self.db,
                mill_id=self.selected_mill_id,
                truck_id=self.selected_truck_id,
                purchase_bill_ids=selected_ids,
                created_by="System"
            )

            QMessageBox.information(
                self, "Success",
                f"Delivery invoice {invoice.invoice_number} created successfully\n"
                f"Bills marked as delivered: {len(selected_ids)}"
            )

            self.invoice_created.emit(invoice.id)
            self.clear_form()
            return invoice.id

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create invoice: {str(e)}")
            return None

    def clear_form(self):
        """Clear form"""
        self.mill_combo.setCurrentIndex(0)
        self.truck_combo.setCurrentIndex(0)
        self.deselect_all_bills()
        self.load_undelivered_bills()
        self.update_summary()

    def cancel(self):
        """Cancel"""
        self.clear_form()
