"""
Reports Screen
Generate and view reports for purchase bills and deliveries
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout,
    QDateEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import QDate, Qt
from datetime import datetime
from config.database import get_db
from services.purchase_service import PurchaseService
from services.delivery_service import DeliveryService
from services.farmer_service import FarmerService
from services.rice_mill_service import RiceMillService


class ReportsScreen(QWidget):
    """Screen for generating reports"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Report Type and Date Range Group
        options_group = self._create_options_group()
        main_layout.addWidget(options_group)

        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Date",
            "Reference No",
            "Description",
            "Weight (kg)",
            "Amount (RM)",
            "Status"
        ])

        main_layout.addWidget(self.results_table)

        # Summary Group
        summary_group = self._create_summary_group()
        main_layout.addWidget(summary_group)

        self.setLayout(main_layout)

    def _create_options_group(self) -> QGroupBox:
        """Create options group"""
        group = QGroupBox("Report Options")
        layout = QFormLayout()

        # Report type
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItem("Purchase Bills", "purchase")
        self.report_type_combo.addItem("Delivery Invoices", "delivery")
        self.report_type_combo.addItem("Farmer Summary", "farmer")
        self.report_type_combo.addItem("Mill Summary", "mill")
        self.report_type_combo.currentIndexChanged.connect(self.on_report_type_changed)
        layout.addRow("Report Type:", self.report_type_combo)

        # Date range
        date_layout = QHBoxLayout()
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.from_date)

        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.to_date)

        layout.addRow("Date Range:", date_layout)

        # Filter
        self.filter_combo = QComboBox()
        self.load_filters()
        layout.addRow("Filter By:", self.filter_combo)

        # Buttons
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Generate Report")
        generate_btn.setStyleSheet("background-color: #007ACC; color: white;")
        generate_btn.clicked.connect(self.generate_report)
        button_layout.addWidget(generate_btn)

        export_btn = QPushButton("Export to Excel")
        export_btn.setStyleSheet("background-color: #28a745; color: white;")
        export_btn.clicked.connect(self.export_excel)
        button_layout.addWidget(export_btn)

        export_pdf_btn = QPushButton("Export to PDF")
        export_pdf_btn.setStyleSheet("background-color: #dc3545; color: white;")
        export_pdf_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(export_pdf_btn)

        button_layout.addStretch()
        layout.addRow(button_layout)

        group.setLayout(layout)
        return group

    def _create_summary_group(self) -> QGroupBox:
        """Create summary group"""
        group = QGroupBox("Summary")
        layout = QFormLayout()

        self.count_label = QLabel("0")
        layout.addRow("Total Records:", self.count_label)

        self.weight_label = QLabel("0.00 kg")
        layout.addRow("Total Weight:", self.weight_label)

        self.amount_label = QLabel("RM 0.00")
        layout.addRow("Total Amount:", self.amount_label)

        group.setLayout(layout)
        return group

    def load_filters(self):
        """Load filter options"""
        self.filter_combo.clear()
        self.filter_combo.addItem("All", None)

        report_type = self.report_type_combo.currentData()

        if report_type == "farmer":
            farmers = FarmerService.get_all(self.db, active_only=True)
            for farmer in farmers:
                self.filter_combo.addItem(farmer.name, farmer.id)
        elif report_type == "mill":
            mills = RiceMillService.get_all(self.db, active_only=True)
            for mill in mills:
                self.filter_combo.addItem(mill.mill_name, mill.id)

    def on_report_type_changed(self):
        """Handle report type change"""
        self.load_filters()

    def generate_report(self):
        """Generate report"""
        report_type = self.report_type_combo.currentData()

        from_date = self.from_date.date().toPyDate()
        to_date = self.to_date.date().toPyDate()
        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())

        if report_type == "purchase":
            self._generate_purchase_report(from_datetime, to_datetime)
        elif report_type == "delivery":
            self._generate_delivery_report(from_datetime, to_datetime)
        elif report_type == "farmer":
            self._generate_farmer_report()
        elif report_type == "mill":
            self._generate_mill_report()

    def _generate_purchase_report(self, from_date, to_date):
        """Generate purchase bill report"""
        bills = PurchaseService.get_by_date_range(self.db, from_date, to_date)

        self.results_table.setRowCount(len(bills))
        total_weight = 0
        total_amount = 0

        for row, bill in enumerate(bills):
            date_str = bill.bill_date.strftime("%d/%m/%Y")
            self.results_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.results_table.setItem(row, 1, QTableWidgetItem(bill.bill_number))

            farmer_name = bill.farmer.name if bill.farmer else "Unknown"
            self.results_table.setItem(row, 2, QTableWidgetItem(farmer_name))

            weight = float(bill.net_weight)
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{weight:,.2f}"))

            amount = float(bill.total_payment)
            self.results_table.setItem(row, 4, QTableWidgetItem(f"RM {amount:,.2f}"))

            status = "Delivered" if bill.is_delivered else "Pending"
            self.results_table.setItem(row, 5, QTableWidgetItem(status))

            total_weight += weight
            total_amount += amount

        self.count_label.setText(str(len(bills)))
        self.weight_label.setText(f"{total_weight:,.2f} kg")
        self.amount_label.setText(f"RM {total_amount:,.2f}")

    def _generate_delivery_report(self, from_date, to_date):
        """Generate delivery invoice report"""
        invoices = DeliveryService.get_by_date_range(self.db, from_date, to_date)

        self.results_table.setRowCount(len(invoices))
        total_weight = 0
        total_bills = 0

        for row, invoice in enumerate(invoices):
            date_str = invoice.invoice_date.strftime("%d/%m/%Y")
            self.results_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.results_table.setItem(row, 1, QTableWidgetItem(invoice.invoice_number))

            mill_name = invoice.mill.mill_name if invoice.mill else "Unknown"
            self.results_table.setItem(row, 2, QTableWidgetItem(mill_name))

            weight = float(invoice.total_weight)
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{weight:,.2f}"))

            items = DeliveryService.get_items(self.db, invoice.id)
            bills_str = f"{len(items)} bills"
            self.results_table.setItem(row, 4, QTableWidgetItem(bills_str))

            self.results_table.setItem(row, 5, QTableWidgetItem("Delivered"))

            total_weight += weight
            total_bills += len(items)

        self.count_label.setText(str(len(invoices)))
        self.weight_label.setText(f"{total_weight:,.2f} kg")
        self.amount_label.setText(f"{total_bills} bills")

    def _generate_farmer_report(self):
        """Generate farmer summary report"""
        QMessageBox.information(self, "Info", "Farmer report not yet implemented")

    def _generate_mill_report(self):
        """Generate mill summary report"""
        QMessageBox.information(self, "Info", "Mill report not yet implemented")

    def export_excel(self):
        """Export report to Excel"""
        QMessageBox.information(self, "Info", "Excel export not yet implemented")

    def export_pdf(self):
        """Export report to PDF"""
        QMessageBox.information(self, "Info", "PDF export not yet implemented")
