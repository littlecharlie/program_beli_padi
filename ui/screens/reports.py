"""
Reports Screen
Generate and view reports for purchase bills and deliveries
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout,
    QDateEdit, QComboBox, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QDate, Qt
from datetime import datetime
from pathlib import Path
import os
import subprocess
import platform

from config.database import get_db
from services.purchase_service import PurchaseService
from services.delivery_service import DeliveryService
from services.farmer_service import FarmerService
from services.rice_mill_service import RiceMillService
from services.pdf_export_service import PdfExportService, PdfExportError, InvalidDateRangeError
from sqlalchemy import func
from models.purchase_bill import PurchaseBill
from models.delivery_invoice import DeliveryInvoice


class ReportsScreen(QWidget):
    """Screen for generating reports"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.current_report_data = None  # Store generated report data for export
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

        # Store report parameters for PDF export
        self.current_report_data = {
            'type': report_type,
            'from_date': from_date,
            'to_date': to_date,
            'filter_id': self.filter_combo.currentData()
        }

        if report_type == "purchase":
            self._generate_purchase_report(from_datetime, to_datetime)
        elif report_type == "delivery":
            self._generate_delivery_report(from_datetime, to_datetime)
        elif report_type == "farmer":
            self._generate_farmer_report(from_date, to_date)
        elif report_type == "mill":
            self._generate_mill_report(from_date, to_date)

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

    def _generate_farmer_report(self, from_date, to_date):
        """Generate farmer summary report"""
        filter_id = self.filter_combo.currentData()

        # Build query
        query = self.db.query(
            PurchaseBill.farmer_id,
            func.count(PurchaseBill.id).label('bill_count'),
            func.sum(PurchaseBill.net_weight).label('total_weight'),
            func.sum(PurchaseBill.total_payment).label('total_payment')
        ).filter(
            PurchaseBill.bill_date >= from_date,
            PurchaseBill.bill_date <= to_date
        )

        if filter_id:
            query = query.filter(PurchaseBill.farmer_id == filter_id)

        farmer_stats = query.group_by(PurchaseBill.farmer_id).all()

        # Update table
        self.results_table.setRowCount(len(farmer_stats))
        total_bills = 0
        total_weight = 0
        total_payment = 0

        for row, stat in enumerate(farmer_stats):
            farmer = FarmerService.get_by_id(self.db, stat.farmer_id)

            self.results_table.setItem(row, 0, QTableWidgetItem("-"))
            self.results_table.setItem(row, 1, QTableWidgetItem(farmer.ic_number if farmer else "N/A"))
            self.results_table.setItem(row, 2, QTableWidgetItem(farmer.name if farmer else "Unknown"))

            weight = float(stat.total_weight) if stat.total_weight else 0
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{weight:,.2f}"))

            payment = float(stat.total_payment) if stat.total_payment else 0
            self.results_table.setItem(row, 4, QTableWidgetItem(f"RM {payment:,.2f}"))

            self.results_table.setItem(row, 5, QTableWidgetItem(f"{stat.bill_count} bills"))

            total_bills += stat.bill_count
            total_weight += weight
            total_payment += payment

        self.count_label.setText(f"{len(farmer_stats)} farmers")
        self.weight_label.setText(f"{total_weight:,.2f} kg")
        self.amount_label.setText(f"RM {total_payment:,.2f}")

    def _generate_mill_report(self, from_date, to_date):
        """Generate mill summary report"""
        filter_id = self.filter_combo.currentData()

        # Build query
        query = self.db.query(
            DeliveryInvoice.mill_id,
            func.count(DeliveryInvoice.id).label('invoice_count'),
            func.sum(DeliveryInvoice.total_weight).label('total_weight')
        ).filter(
            DeliveryInvoice.invoice_date >= from_date,
            DeliveryInvoice.invoice_date <= to_date
        )

        if filter_id:
            query = query.filter(DeliveryInvoice.mill_id == filter_id)

        mill_stats = query.group_by(DeliveryInvoice.mill_id).all()

        # Update table
        self.results_table.setRowCount(len(mill_stats))
        total_invoices = 0
        total_weight = 0

        for row, stat in enumerate(mill_stats):
            mill = RiceMillService.get_by_id(self.db, stat.mill_id)

            self.results_table.setItem(row, 0, QTableWidgetItem("-"))
            self.results_table.setItem(row, 1, QTableWidgetItem(mill.mill_code if mill and mill.mill_code else "N/A"))
            self.results_table.setItem(row, 2, QTableWidgetItem(mill.mill_name if mill else "Unknown"))

            weight = float(stat.total_weight) if stat.total_weight else 0
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{weight:,.2f}"))

            self.results_table.setItem(row, 4, QTableWidgetItem(f"{stat.invoice_count} invoices"))
            self.results_table.setItem(row, 5, QTableWidgetItem("Delivered"))

            total_invoices += stat.invoice_count
            total_weight += weight

        self.count_label.setText(f"{len(mill_stats)} mills")
        self.weight_label.setText(f"{total_weight:,.2f} kg")
        self.amount_label.setText(f"{total_invoices} invoices")

    def export_excel(self):
        """Export report to Excel"""
        QMessageBox.information(self, "Info", "Excel export not yet implemented")

    def export_pdf(self):
        """Export report to PDF"""
        if not self.current_report_data:
            QMessageBox.warning(
                self,
                "No Report Generated",
                "Please generate a report first before exporting to PDF."
            )
            return

        report_type = self.current_report_data['type']
        from_date = self.current_report_data['from_date']
        to_date = self.current_report_data['to_date']
        filter_id = self.current_report_data['filter_id']

        try:
            # Ask user where to save
            default_filename = self._get_default_filename(report_type, from_date, to_date)
            default_dir = str(Path.home() / "Documents")

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Report as PDF",
                str(Path(default_dir) / default_filename),
                "PDF Files (*.pdf);;All Files (*.*)"
            )

            if not file_path:
                return  # User cancelled

            # Ensure .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'

            # Generate appropriate PDF based on report type
            if report_type == "purchase":
                output_path = PdfExportService.export_date_range_report(
                    db=self.db,
                    start_date=from_date,
                    end_date=to_date,
                    report_type='purchase',
                    output_path=file_path,
                    return_bytes=False
                )
            elif report_type == "delivery":
                output_path = PdfExportService.export_date_range_report(
                    db=self.db,
                    start_date=from_date,
                    end_date=to_date,
                    report_type='delivery',
                    output_path=file_path,
                    return_bytes=False
                )
            elif report_type == "farmer":
                output_path = PdfExportService.export_farmer_summary_report(
                    db=self.db,
                    start_date=from_date,
                    end_date=to_date,
                    farmer_id=filter_id,
                    output_path=file_path,
                    return_bytes=False
                )
            elif report_type == "mill":
                output_path = PdfExportService.export_mill_summary_report(
                    db=self.db,
                    start_date=from_date,
                    end_date=to_date,
                    mill_id=filter_id,
                    output_path=file_path,
                    return_bytes=False
                )
            else:
                raise PdfExportError(f"Unknown report type: {report_type}")

            # Show success message
            reply = QMessageBox.question(
                self,
                "Export Successful",
                f"Report exported successfully to:\n{output_path}\n\nWould you like to open the PDF file?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self._open_file(output_path)

        except InvalidDateRangeError as e:
            QMessageBox.critical(
                self,
                "Invalid Date Range",
                f"Invalid date range: {str(e)}"
            )
        except PdfExportError as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export PDF:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred:\n{str(e)}"
            )

    def _get_default_filename(self, report_type: str, from_date, to_date) -> str:
        """Generate default filename for PDF export"""
        date_str = f"{from_date.strftime('%Y%m%d')}_{to_date.strftime('%Y%m%d')}"

        if report_type == "purchase":
            return f"purchase_bills_report_{date_str}.pdf"
        elif report_type == "delivery":
            return f"delivery_invoices_report_{date_str}.pdf"
        elif report_type == "farmer":
            return f"farmer_summary_report_{date_str}.pdf"
        elif report_type == "mill":
            return f"mill_summary_report_{date_str}.pdf"
        else:
            return f"report_{date_str}.pdf"

    def _open_file(self, file_path: str):
        """Open file with default system application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Cannot Open File",
                f"File saved successfully but could not be opened automatically:\n{str(e)}\n\nPlease open the file manually:\n{file_path}"
            )
