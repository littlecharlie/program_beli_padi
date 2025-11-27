"""
Purchase Bill Edit Dialog
Dialog for editing existing purchase bills
"""
from typing import Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QDoubleSpinBox, QPushButton, QMessageBox,
    QFormLayout, QTextEdit, QComboBox
)
from PyQt5.QtCore import Qt
from decimal import Decimal
from datetime import datetime
from config.database import get_db
from services.farmer_service import FarmerService
from services.truck_service import TruckService
from services.harvest_area_service import HarvestAreaService
from services.purchase_service import PurchaseService
from services.calculation_service import CalculationService
from models.purchase_bill import PurchaseBill


class PurchaseEditDialog(QDialog):
    """Dialog for editing purchase bills"""

    # Enhanced dropdown styling
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

    def __init__(self, bill_id: int, parent=None):
        """
        Initialize edit dialog

        Args:
            bill_id: ID of purchase bill to edit
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = get_db()
        self.bill_id = bill_id
        self.bill: Optional[PurchaseBill] = None

        self.setWindowTitle("Edit Purchase Bill")
        self.setModal(True)
        self.setMinimumWidth(600)

        # Load bill data
        self.load_bill()

        if not self.bill:
            QMessageBox.critical(self, "Error", "Failed to load purchase bill")
            self.reject()
            return

        # Check if bill can be edited
        if self.bill.is_delivered:
            QMessageBox.warning(
                self, "Cannot Edit",
                "This bill has already been delivered and cannot be edited."
            )
            self.reject()
            return

        self.setup_ui()
        self.populate_fields()

    def load_bill(self):
        """Load bill from database"""
        self.bill = PurchaseService.get_by_id(self.db, self.bill_id)

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout()

        # Title
        title = QLabel(f"Edit Purchase Bill: {self.bill.bill_number}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Bill Information Group (Read-only)
        bill_info_group = self._create_bill_info_group()
        layout.addWidget(bill_info_group)

        # Farmer Information Group (Read-only)
        farmer_group = self._create_farmer_group()
        layout.addWidget(farmer_group)

        # Weighing Information Group (Read-only)
        weighing_group = self._create_weighing_group()
        layout.addWidget(weighing_group)

        # Discount Information Group (Editable)
        discount_group = self._create_discount_group()
        layout.addWidget(discount_group)

        # Calculations Group (Read-only, auto-updates)
        calcs_group = self._create_calculations_group()
        layout.addWidget(calcs_group)

        # Additional Information Group (Editable)
        additional_group = self._create_additional_group()
        layout.addWidget(additional_group)

        # Button Group
        button_layout = self._create_button_group()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_bill_info_group(self) -> QGroupBox:
        """Create bill information group"""
        group = QGroupBox("Bill Information")
        layout = QFormLayout()

        self.bill_number_input = QLineEdit()
        self.bill_number_input.setReadOnly(True)

        self.bill_date_input = QLineEdit()
        self.bill_date_input.setReadOnly(True)

        self.status_input = QLineEdit()
        self.status_input.setReadOnly(True)

        layout.addRow("Bill Number:", self.bill_number_input)
        layout.addRow("Date/Time:", self.bill_date_input)
        layout.addRow("Status:", self.status_input)

        group.setLayout(layout)
        return group

    def _create_farmer_group(self) -> QGroupBox:
        """Create farmer information group"""
        group = QGroupBox("Farmer Information (Read-Only)")
        layout = QFormLayout()

        self.farmer_name_input = QLineEdit()
        self.farmer_name_input.setReadOnly(True)

        self.farmer_ic_input = QLineEdit()
        self.farmer_ic_input.setReadOnly(True)

        self.farmer_reg_input = QLineEdit()
        self.farmer_reg_input.setReadOnly(True)

        layout.addRow("Farmer Name:", self.farmer_name_input)
        layout.addRow("IC Number:", self.farmer_ic_input)
        layout.addRow("Registration No:", self.farmer_reg_input)

        group.setLayout(layout)
        return group

    def _create_weighing_group(self) -> QGroupBox:
        """Create weighing information group"""
        group = QGroupBox("Weighing Information (Read-Only)")
        layout = QFormLayout()

        self.truck_input = QLineEdit()
        self.truck_input.setReadOnly(True)

        self.weighbridge_input = QLineEdit()
        self.weighbridge_input.setPlaceholderText("Optional weighbridge receipt number")

        self.gross_weight_input = QLineEdit()
        self.gross_weight_input.setReadOnly(True)

        layout.addRow("Truck:", self.truck_input)
        layout.addRow("Weighbridge No:", self.weighbridge_input)
        layout.addRow("Gross Weight:", self.gross_weight_input)

        group.setLayout(layout)
        return group

    def _create_discount_group(self) -> QGroupBox:
        """Create discount information group (editable)"""
        group = QGroupBox("Discounts (Editable)")
        layout = QFormLayout()

        # Note about locked defaults
        note = QLabel("Note: Discount percentages are set to system defaults and locked.")
        note.setStyleSheet("color: #ffa500; font-size: 10px; padding: 5px;")
        layout.addRow(note)

        # Wap Basah (moisture)
        self.wap_basah_input = QDoubleSpinBox()
        self.wap_basah_input.setRange(0, 100)
        self.wap_basah_input.setDecimals(2)
        self.wap_basah_input.setSuffix(" %")
        self.wap_basah_input.setReadOnly(True)
        self.wap_basah_input.valueChanged.connect(self.on_calculation_changed)
        layout.addRow("Wap Basah (Moisture):", self.wap_basah_input)

        # Hampa Padi (empty grains)
        self.hampa_padi_input = QDoubleSpinBox()
        self.hampa_padi_input.setRange(0, 100)
        self.hampa_padi_input.setDecimals(2)
        self.hampa_padi_input.setSuffix(" %")
        self.hampa_padi_input.setReadOnly(True)
        self.hampa_padi_input.valueChanged.connect(self.on_calculation_changed)
        layout.addRow("Hampa Padi (Empty Grains):", self.hampa_padi_input)

        # Padi Muda/Rosak (damaged rice)
        self.padi_muda_input = QDoubleSpinBox()
        self.padi_muda_input.setRange(0, 100)
        self.padi_muda_input.setDecimals(2)
        self.padi_muda_input.setSuffix(" %")
        self.padi_muda_input.setReadOnly(True)
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
        group = QGroupBox("Calculations (Auto-Updated)")
        layout = QFormLayout()

        self.discount_weight_input = QLineEdit()
        self.discount_weight_input.setReadOnly(True)

        self.net_weight_input = QLineEdit()
        self.net_weight_input.setReadOnly(True)

        self.rice_price_input = QLineEdit()
        self.rice_price_input.setReadOnly(True)

        self.total_payment_input = QLineEdit()
        self.total_payment_input.setReadOnly(True)

        self.subsidy_estimate_input = QLineEdit()
        self.subsidy_estimate_input.setReadOnly(True)

        layout.addRow("Discount Weight:", self.discount_weight_input)
        layout.addRow("Net Weight:", self.net_weight_input)
        layout.addRow("Price/1000kg:", self.rice_price_input)
        layout.addRow("Total Payment:", self.total_payment_input)
        layout.addRow("Subsidy Estimate:", self.subsidy_estimate_input)

        group.setLayout(layout)
        return group

    def _create_additional_group(self) -> QGroupBox:
        """Create additional information group (editable)"""
        group = QGroupBox("Additional Information (Editable)")
        layout = QFormLayout()

        # Harvest area
        self.harvest_area_combo = QComboBox()
        self.harvest_area_combo.setStyleSheet(self.COMBO_BOX_STYLE)
        self.load_harvest_areas()
        layout.addRow("Harvest Area:", self.harvest_area_combo)

        group.setLayout(layout)
        return group

    def _create_button_group(self) -> QHBoxLayout:
        """Create button group"""
        layout = QHBoxLayout()

        # Save button (primary - green)
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px;")
        self.save_btn.clicked.connect(self.save_changes)

        # Cancel button (neutral - gray)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px;")
        self.cancel_btn.clicked.connect(self.reject)

        layout.addStretch()
        layout.addWidget(self.save_btn)
        layout.addWidget(self.cancel_btn)

        return layout

    def load_harvest_areas(self):
        """Load harvest areas into combo box"""
        areas = HarvestAreaService.get_all(self.db)
        self.harvest_area_combo.addItem("(None)", None)
        for area in areas:
            self.harvest_area_combo.addItem(area.area_name, area.id)

    def populate_fields(self):
        """Populate fields with bill data"""
        # Bill info
        self.bill_number_input.setText(self.bill.bill_number)
        self.bill_date_input.setText(self.bill.bill_date.strftime("%d/%m/%Y %H:%M"))
        status = "Delivered" if self.bill.is_delivered else "Pending"
        self.status_input.setText(status)

        # Farmer info
        if self.bill.farmer:
            self.farmer_name_input.setText(self.bill.farmer.name or "")
            self.farmer_ic_input.setText(self.bill.farmer.ic_number or "")
            self.farmer_reg_input.setText(self.bill.farmer.registration_number or "")

        # Weighing info
        if self.bill.truck:
            self.truck_input.setText(self.bill.truck.truck_number or "")
        self.weighbridge_input.setText(self.bill.weighbridge_receipt or "")
        self.gross_weight_input.setText(f"{float(self.bill.gross_weight):,.2f} kg")

        # Discounts
        self.wap_basah_input.setValue(float(self.bill.discount_wap_basah))
        self.hampa_padi_input.setValue(float(self.bill.discount_hampa_padi))
        self.padi_muda_input.setValue(float(self.bill.discount_padi_muda))

        # Harvest area
        if self.bill.harvest_area_id:
            index = self.harvest_area_combo.findData(self.bill.harvest_area_id)
            if index >= 0:
                self.harvest_area_combo.setCurrentIndex(index)

        # Update calculations
        self.update_calculations()

    def on_calculation_changed(self):
        """Recalculate when values change"""
        self.update_calculations()

    def update_calculations(self):
        """Update all calculations"""
        try:
            gross_weight = float(self.bill.gross_weight)
            wap_basah = self.wap_basah_input.value()
            hampa_padi = self.hampa_padi_input.value()
            padi_muda = self.padi_muda_input.value()
            rice_price = float(self.bill.rice_price_per_1000kg)

            # Calculate
            calcs = CalculationService.calculate_purchase_bill(
                gross_weight, wap_basah, hampa_padi, padi_muda, rice_price
            )

            # Update displays
            self.total_discount_input.setText(f"{calcs['total_discount_percent']:.2f} %")
            self.discount_weight_input.setText(f"{calcs['discount_weight']:,.2f} kg")
            self.net_weight_input.setText(f"{calcs['net_weight']:,.2f} kg")
            self.rice_price_input.setText(f"RM {rice_price:,.2f}")
            self.total_payment_input.setText(f"RM {calcs['total_payment']:,.2f}")
            self.subsidy_estimate_input.setText(f"RM {calcs['subsidy_estimate']:,.2f}")

        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", str(e))

    def save_changes(self):
        """Save changes to database"""
        try:
            # Prepare update data
            update_data = {
                'discount_wap_basah': self.wap_basah_input.value(),
                'discount_hampa_padi': self.hampa_padi_input.value(),
                'discount_padi_muda': self.padi_muda_input.value(),
                'weighbridge_receipt': self.weighbridge_input.text() or None,
                'harvest_area_id': self.harvest_area_combo.currentData()
            }

            # Update bill
            updated_bill = PurchaseService.update(self.db, self.bill_id, **update_data)

            if updated_bill:
                QMessageBox.information(
                    self, "Success",
                    f"Purchase bill {self.bill.bill_number} updated successfully"
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "Failed to update purchase bill"
                )

        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to save changes: {str(e)}"
            )
