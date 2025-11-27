"""
Purchase Entry Screen
UI for creating and editing purchase bills
"""
from typing import Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox,
    QComboBox, QFormLayout, QTextEdit, QScrollArea, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from config.database import get_db
from services.farmer_service import FarmerService
from services.truck_service import TruckService
from services.harvest_area_service import HarvestAreaService
from services.purchase_service import PurchaseService
from services.calculation_service import CalculationService
from services.config_service import ConfigService
from services.receipt_data_service import ReceiptDataService
from utils.validators import Validators
from ui.widgets.farmer_selector import FarmerSelectorWidget
from ui.widgets.truck_selector import TruckSelectorWidget
from printing.purchase_formatter import PurchaseReceiptFormatter
from printing.printer_manager import PrinterManager


class PurchaseEntryScreen(QWidget):
    """Screen for entering purchase bills"""

    # Signal when bill is saved
    bill_saved = pyqtSignal(int)  # bill_id

    # Enhanced dropdown styling consistent with TruckSelectorWidget
    COMBO_BOX_STYLE = """
        QComboBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #4a4a4a;
            padding: 8px 30px 8px 8px;
            border-radius: 4px;
            min-height: 28px;
        }

        QComboBox:focus {
            border: 2px solid #4da6ff;
        }

        QComboBox:disabled {
            background-color: #1e1e1e;
            color: #666666;
        }

        QComboBox::drop-down {
            border: none;
            width: 30px;
            background-color: transparent;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #e0e0e0;
            width: 0px;
            height: 0px;
            margin-right: 8px;
        }

        QComboBox::down-arrow:hover {
            border-top: 6px solid #4da6ff;
        }

        QComboBox::down-arrow:disabled {
            border-top: 6px solid #666666;
        }

        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #4a4a4a;
            selection-background-color: #4da6ff;
            selection-color: white;
            padding: 4px;
            outline: none;
        }

        QComboBox QAbstractItemView::item {
            padding: 8px;
            min-height: 25px;
        }

        QComboBox QAbstractItemView::item:hover {
            background-color: #404040;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.selected_farmer_id = None
        self.selected_truck_id = None
        self.current_bill = None
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("New Purchase Bill")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Bill Information Group
        bill_info_group = self._create_bill_info_group()
        scroll_layout.addWidget(bill_info_group)

        # Farmer Information Group
        farmer_group = self._create_farmer_group()
        scroll_layout.addWidget(farmer_group)

        # Weighing Information Group
        weighing_group = self._create_weighing_group()
        scroll_layout.addWidget(weighing_group)

        # Discount Information Group
        discount_group = self._create_discount_group()
        scroll_layout.addWidget(discount_group)

        # Calculations Group (Read-only)
        calcs_group = self._create_calculations_group()
        scroll_layout.addWidget(calcs_group)

        # Additional Information Group
        additional_group = self._create_additional_group()
        scroll_layout.addWidget(additional_group)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Button Group
        button_layout = self._create_button_group()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_bill_info_group(self) -> QGroupBox:
        """Create bill information group"""
        group = QGroupBox("Bill Information")
        layout = QFormLayout()

        self.bill_number_input = QLineEdit()
        self.bill_number_input.setReadOnly(True)
        self.bill_number_input.setText("(Auto-generated)")

        self.bill_date_input = QLineEdit()
        self.bill_date_input.setReadOnly(True)
        self.bill_date_input.setText(datetime.now().strftime("%d/%m/%Y %H:%M"))

        layout.addRow("Bill Number:", self.bill_number_input)
        layout.addRow("Date/Time:", self.bill_date_input)

        group.setLayout(layout)
        return group

    def _create_farmer_group(self) -> QGroupBox:
        """Create farmer selection group"""
        group = QGroupBox("Farmer Information")
        layout = QVBoxLayout()

        # Farmer selector widget
        self.farmer_selector = FarmerSelectorWidget()
        self.farmer_selector.farmer_selected.connect(self.on_farmer_selected)
        layout.addWidget(self.farmer_selector)

        # Farmer details (read-only)
        details_layout = QFormLayout()

        self.farmer_reg_input = QLineEdit()
        self.farmer_reg_input.setReadOnly(True)

        self.farmer_subsidy_input = QLineEdit()
        self.farmer_subsidy_input.setReadOnly(True)

        self.farmer_address_input = QTextEdit()
        self.farmer_address_input.setReadOnly(True)
        self.farmer_address_input.setMaximumHeight(60)

        details_layout.addRow("Registration No:", self.farmer_reg_input)
        details_layout.addRow("Subsidy Code:", self.farmer_subsidy_input)
        details_layout.addRow("Address:", self.farmer_address_input)

        layout.addLayout(details_layout)
        group.setLayout(layout)
        return group

    def _create_weighing_group(self) -> QGroupBox:
        """Create weighing information group"""
        group = QGroupBox("Weighing Information")
        layout = QFormLayout()

        # Truck selector
        self.truck_selector = TruckSelectorWidget()
        self.truck_selector.truck_selected.connect(self.on_truck_selected)
        layout.addRow("Truck:", self.truck_selector)

        # Weighbridge receipt
        self.weighbridge_input = QLineEdit()
        self.weighbridge_input.setPlaceholderText("Optional weighbridge receipt number")
        layout.addRow("Weighbridge No:", self.weighbridge_input)

        # Gross weight
        self.gross_weight_input = QDoubleSpinBox()
        self.gross_weight_input.setRange(0.01, 1000000)
        self.gross_weight_input.setDecimals(2)
        self.gross_weight_input.setSuffix(" kg")
        self.gross_weight_input.setToolTip("Must be greater than 0")
        self.gross_weight_input.valueChanged.connect(self.on_calculation_changed)
        layout.addRow("Gross Weight:", self.gross_weight_input)

        group.setLayout(layout)
        return group

    def _create_discount_group(self) -> QGroupBox:
        """Create discount information group"""
        group = QGroupBox("Discounts")
        layout = QFormLayout()

        # Wap Basah (moisture)
        self.wap_basah_input = QDoubleSpinBox()
        self.wap_basah_input.setRange(0, 100)
        self.wap_basah_input.setDecimals(2)
        self.wap_basah_input.setValue(7.00)
        self.wap_basah_input.setSuffix(" %")
        self.wap_basah_input.setReadOnly(True)  # Lock field
        self.wap_basah_input.valueChanged.connect(self.on_calculation_changed)
        layout.addRow("Wap Basah (Moisture):", self.wap_basah_input)

        # Hampa Padi (empty grains)
        self.hampa_padi_input = QDoubleSpinBox()
        self.hampa_padi_input.setRange(0, 100)
        self.hampa_padi_input.setDecimals(2)
        self.hampa_padi_input.setValue(7.00)
        self.hampa_padi_input.setSuffix(" %")
        self.hampa_padi_input.setReadOnly(True)  # Lock field
        self.hampa_padi_input.valueChanged.connect(self.on_calculation_changed)
        layout.addRow("Hampa Padi (Empty Grains):", self.hampa_padi_input)

        # Padi Muda/Rosak (damaged rice)
        self.padi_muda_input = QDoubleSpinBox()
        self.padi_muda_input.setRange(0, 100)
        self.padi_muda_input.setDecimals(2)
        self.padi_muda_input.setValue(6.00)
        self.padi_muda_input.setSuffix(" %")
        self.padi_muda_input.setReadOnly(True)  # Lock field
        self.padi_muda_input.valueChanged.connect(self.on_calculation_changed)
        layout.addRow("Padi Muda/Rosak (Damaged):", self.padi_muda_input)

        # Total discount
        self.total_discount_input = QLineEdit()
        self.total_discount_input.setReadOnly(True)
        layout.addRow("Total Discount:", self.total_discount_input)

        group.setLayout(layout)
        return group

    def _create_calculations_group(self) -> QGroupBox:
        """Create calculations group (read-only)"""
        group = QGroupBox("Calculations (Auto)")
        layout = QFormLayout()

        self.discount_weight_input = QLineEdit()
        self.discount_weight_input.setReadOnly(True)
        layout.addRow("Discount Weight:", self.discount_weight_input)

        self.net_weight_input = QLineEdit()
        self.net_weight_input.setReadOnly(True)
        layout.addRow("Net Weight:", self.net_weight_input)

        self.rice_price_input = QLineEdit()
        self.rice_price_input.setReadOnly(True)
        layout.addRow("Price/1000kg:", self.rice_price_input)

        self.total_payment_input = QLineEdit()
        self.total_payment_input.setReadOnly(True)
        layout.addRow("Total Payment:", self.total_payment_input)

        self.subsidy_estimate_input = QLineEdit()
        self.subsidy_estimate_input.setReadOnly(True)
        layout.addRow("Subsidy Estimate:", self.subsidy_estimate_input)

        group.setLayout(layout)
        return group

    def _create_additional_group(self) -> QGroupBox:
        """Create additional information group"""
        group = QGroupBox("Additional Information")
        layout = QFormLayout()

        # Harvest area
        self.harvest_area_combo = QComboBox()
        self.harvest_area_combo.setStyleSheet(self.COMBO_BOX_STYLE)  # Apply enhanced styling
        self.load_harvest_areas()
        layout.addRow("Harvest Area:", self.harvest_area_combo)

        group.setLayout(layout)
        return group

    def _create_button_group(self) -> QHBoxLayout:
        """Create button group"""
        layout = QHBoxLayout()

        # Save & Print button (primary action - green)
        self.save_and_print_btn = QPushButton("Save & Print")
        self.save_and_print_btn.setStyleSheet("background-color: #28a745; color: white;")
        self.save_and_print_btn.clicked.connect(self.save_and_print)

        # Save Only button (secondary action - blue)
        self.save_only_btn = QPushButton("Save Only")
        self.save_only_btn.setStyleSheet("background-color: #007ACC; color: white;")
        self.save_only_btn.clicked.connect(self.save_only)

        # Print button (tertiary action - purple/info)
        self.print_btn = QPushButton("Print Receipt")
        self.print_btn.setStyleSheet("background-color: #9c27b0; color: white;")
        self.print_btn.clicked.connect(self.print_receipt)
        self.print_btn.setEnabled(False)  # Disabled until a bill is saved
        self.print_btn.setToolTip("Save a bill first to print its receipt")

        # Cancel button (neutral - gray)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #6c757d; color: white;")
        self.cancel_btn.clicked.connect(self.cancel)

        # Layout: [Save & Print] [Save Only] [Print] <stretch> [Cancel]
        layout.addWidget(self.save_and_print_btn)
        layout.addWidget(self.save_only_btn)
        layout.addWidget(self.print_btn)
        layout.addStretch()
        layout.addWidget(self.cancel_btn)

        return layout

    def load_config(self):
        """Load configuration from database"""
        rice_price = ConfigService.get_float_value(
            self.db, 'rice_price_per_1000kg', 1500.00
        )
        self.rice_price_input.setText(f"RM {rice_price:,.2f}")
        self.rice_price = rice_price

    def load_harvest_areas(self):
        """Load harvest areas into combo box"""
        areas = HarvestAreaService.get_all(self.db)
        for area in areas:
            self.harvest_area_combo.addItem(area.area_name, area.id)

    def on_farmer_selected(self, farmer_id: int, name: str, ic: str):
        """Handle farmer selection"""
        self.selected_farmer_id = farmer_id
        farmer = FarmerService.get_by_id(self.db, farmer_id)

        if farmer:
            self.farmer_reg_input.setText(farmer.registration_number or "")
            self.farmer_subsidy_input.setText(farmer.subsidy_code or "")
            self.farmer_address_input.setText(farmer.address or "")

    def on_truck_selected(self, truck_id: int, truck_number: str):
        """Handle truck selection"""
        self.selected_truck_id = truck_id

    def on_calculation_changed(self):
        """Recalculate when values change"""
        self.update_calculations()

    def update_calculations(self):
        """Update all calculations"""
        try:
            gross_weight = self.gross_weight_input.value()
            wap_basah = self.wap_basah_input.value()
            hampa_padi = self.hampa_padi_input.value()
            padi_muda = self.padi_muda_input.value()

            if gross_weight <= 0:
                self.clear_calculations()
                return

            # Validate total discount
            is_valid, error = CalculationService.validate_total_discount(
                wap_basah, hampa_padi, padi_muda
            )

            if not is_valid:
                QMessageBox.warning(self, "Validation Error", error)
                self.clear_calculations()
                return

            # Calculate
            calcs = CalculationService.calculate_purchase_bill(
                gross_weight, wap_basah, hampa_padi, padi_muda,
                self.rice_price
            )

            # Update displays
            self.total_discount_input.setText(f"{calcs['total_discount_percent']:.2f} %")
            self.discount_weight_input.setText(f"{calcs['discount_weight']:,.2f} kg")
            self.net_weight_input.setText(f"{calcs['net_weight']:,.2f} kg")
            self.total_payment_input.setText(f"RM {calcs['total_payment']:,.2f}")
            self.subsidy_estimate_input.setText(f"RM {calcs['subsidy_estimate']:,.2f}")

        except Exception as e:
            self.clear_calculations()
            QMessageBox.critical(self, "Calculation Error", str(e))

    def clear_calculations(self):
        """Clear calculated fields"""
        self.total_discount_input.clear()
        self.discount_weight_input.clear()
        self.net_weight_input.clear()
        self.total_payment_input.clear()
        self.subsidy_estimate_input.clear()

    def validate_inputs(self) -> Tuple[bool, str]:
        """Validate all inputs"""
        if not self.selected_farmer_id:
            return False, "Please select a farmer"

        if not self.selected_truck_id:
            return False, "Please select a truck"

        # Validate gross weight
        is_valid, error = Validators.validate_weight(
            self.gross_weight_input.value(), "Gross Weight"
        )
        if not is_valid:
            return False, error

        # Validate discounts
        for discount_val, name in [
            (self.wap_basah_input.value(), "Wap Basah"),
            (self.hampa_padi_input.value(), "Hampa Padi"),
            (self.padi_muda_input.value(), "Padi Muda/Rosak")
        ]:
            is_valid, error = Validators.validate_percentage(discount_val, name)
            if not is_valid:
                return False, error

        # Validate total discount
        is_valid, error = CalculationService.validate_total_discount(
            self.wap_basah_input.value(),
            self.hampa_padi_input.value(),
            self.padi_muda_input.value()
        )
        if not is_valid:
            return False, error

        return True, ""

    def save_bill(self) -> int:
        """Save purchase bill to database"""
        is_valid, error = self.validate_inputs()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error)
            return None

        try:
            harvest_area_id = self.harvest_area_combo.currentData()

            bill = PurchaseService.create(
                self.db,
                farmer_id=self.selected_farmer_id,
                truck_id=self.selected_truck_id,
                gross_weight=self.gross_weight_input.value(),
                discount_wap_basah=self.wap_basah_input.value(),
                discount_hampa_padi=self.hampa_padi_input.value(),
                discount_padi_muda=self.padi_muda_input.value(),
                rice_price=self.rice_price,
                weighbridge_receipt=self.weighbridge_input.text() or None,
                harvest_area_id=harvest_area_id,
                created_by="System"
            )

            QMessageBox.information(
                self, "Success",
                f"Purchase bill {bill.bill_number} saved successfully"
            )

            self.bill_saved.emit(bill.id)
            self.current_bill = bill

            # Update bill number display
            self.bill_number_input.setText(bill.bill_number)

            # Enable print button now that we have a saved bill
            self.print_btn.setEnabled(True)
            self.print_btn.setToolTip("Print receipt for this purchase bill")

            return bill.id

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save bill: {str(e)}")
            return None

    def print_receipt(self):
        """Print receipt for the current bill"""
        if not self.current_bill:
            QMessageBox.warning(
                self, "No Bill",
                "Please save a bill first before printing."
            )
            return

        try:
            # Prepare receipt data
            receipt_data = ReceiptDataService.prepare_purchase_bill_data(
                self.db, self.current_bill
            )

            # Format receipt for printing
            receipt_text = PurchaseReceiptFormatter.format_receipt_for_printing(receipt_data)

            # Try to print to printer
            print_success = PrinterManager.print_receipt(receipt_text)

            if print_success:
                QMessageBox.information(
                    self, "Print Success",
                    f"Receipt for bill {self.current_bill.bill_number} sent to printer successfully."
                )
            else:
                # Printer failed, offer to save to file
                reply = QMessageBox.question(
                    self, "Printer Unavailable",
                    "Failed to print to printer. Would you like to save the receipt to a file instead?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    self.save_receipt_to_file(receipt_text)

        except Exception as e:
            QMessageBox.critical(
                self, "Print Error",
                f"Failed to print receipt: {str(e)}\n\nWould you like to save to file instead?"
            )
            # Offer to save to file on error
            reply = QMessageBox.question(
                self, "Save to File",
                "Save receipt to file?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    receipt_data = ReceiptDataService.prepare_purchase_bill_data(
                        self.db, self.current_bill
                    )
                    receipt_text = PurchaseReceiptFormatter.format_receipt(receipt_data)
                    self.save_receipt_to_file(receipt_text)
                except Exception as file_error:
                    QMessageBox.critical(
                        self, "Error",
                        f"Failed to save receipt: {str(file_error)}"
                    )

    def save_receipt_to_file(self, receipt_text: str):
        """Save receipt to a text file"""
        try:
            # Create default filename with bill number and timestamp
            default_name = f"receipt_{self.current_bill.bill_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            # Get save location from user
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Receipt to File",
                str(Path.home() / default_name),
                "Text Files (*.txt);;All Files (*)"
            )

            if file_path:
                # Save receipt to file
                success = PrinterManager.print_to_file(receipt_text, file_path)

                if success:
                    QMessageBox.information(
                        self, "File Saved",
                        f"Receipt saved to:\n{file_path}"
                    )
                else:
                    QMessageBox.warning(
                        self, "Save Failed",
                        "Failed to save receipt to file."
                    )

        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to save receipt to file: {str(e)}"
            )

    def save_and_print(self):
        """Save bill and print receipt"""
        bill_id = self.save_bill()
        if bill_id:
            # Print the receipt immediately after saving
            self.print_receipt()

    def save_only(self):
        """Save bill only"""
        self.save_bill()

    def cancel(self):
        """Cancel and clear form"""
        self.farmer_selector.clear_selection()
        self.truck_selector.truck_combo.setCurrentIndex(0)
        self.gross_weight_input.setValue(0)
        self.wap_basah_input.setValue(7.00)
        self.hampa_padi_input.setValue(7.00)
        self.padi_muda_input.setValue(6.00)
        self.weighbridge_input.clear()
        self.clear_calculations()
        self.current_bill = None
        self.bill_number_input.setText("(Auto-generated)")
        self.print_btn.setEnabled(False)
        self.print_btn.setToolTip("Save a bill first to print its receipt")
