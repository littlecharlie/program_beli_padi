"""
Settings Screen
System configuration management
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QMessageBox, QDoubleSpinBox,
    QSpinBox
)
from config.database import get_db
from services.config_service import ConfigService


class SettingsScreen(QWidget):
    """Screen for system settings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("System Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Business Settings Group
        business_group = self._create_business_settings_group()
        main_layout.addWidget(business_group)

        # Company Information Group
        company_group = self._create_company_info_group()
        main_layout.addWidget(company_group)

        # Printer Settings Group
        printer_group = self._create_printer_settings_group()
        main_layout.addWidget(printer_group)

        main_layout.addStretch()

        # Button Group
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("background-color: #28a745; color: white;")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_business_settings_group(self) -> QGroupBox:
        """Create business settings group"""
        group = QGroupBox("Business Settings")
        layout = QFormLayout()

        self.rice_price_input = QDoubleSpinBox()
        self.rice_price_input.setRange(0, 10000)
        self.rice_price_input.setDecimals(2)
        layout.addRow("Rice Price (per 1000kg):", self.rice_price_input)

        self.subsidy_rate_input = QDoubleSpinBox()
        self.subsidy_rate_input.setRange(0, 100)
        self.subsidy_rate_input.setDecimals(2)
        layout.addRow("Subsidy Rate (per kg):", self.subsidy_rate_input)

        self.wap_basah_input = QDoubleSpinBox()
        self.wap_basah_input.setRange(0, 100)
        self.wap_basah_input.setDecimals(2)
        layout.addRow("Default Wap Basah (%):", self.wap_basah_input)

        self.hampa_padi_input = QDoubleSpinBox()
        self.hampa_padi_input.setRange(0, 100)
        self.hampa_padi_input.setDecimals(2)
        layout.addRow("Default Hampa Padi (%):", self.hampa_padi_input)

        self.padi_muda_input = QDoubleSpinBox()
        self.padi_muda_input.setRange(0, 100)
        self.padi_muda_input.setDecimals(2)
        layout.addRow("Default Padi Muda (%):", self.padi_muda_input)

        group.setLayout(layout)
        return group

    def _create_company_info_group(self) -> QGroupBox:
        """Create company information group"""
        group = QGroupBox("Company Information")
        layout = QFormLayout()

        self.company_name_input = QLineEdit()
        layout.addRow("Company Name:", self.company_name_input)

        self.company_address1_input = QLineEdit()
        layout.addRow("Address Line 1:", self.company_address1_input)

        self.company_address2_input = QLineEdit()
        layout.addRow("Address Line 2:", self.company_address2_input)

        self.company_reg_input = QLineEdit()
        layout.addRow("Registration Number:", self.company_reg_input)

        self.company_phone_input = QLineEdit()
        layout.addRow("Phone Number:", self.company_phone_input)

        self.manager_name_input = QLineEdit()
        layout.addRow("Manager Name:", self.manager_name_input)

        group.setLayout(layout)
        return group

    def _create_printer_settings_group(self) -> QGroupBox:
        """Create printer settings group"""
        group = QGroupBox("Printer Settings")
        layout = QFormLayout()

        self.printer_name_input = QLineEdit()
        layout.addRow("Printer Name:", self.printer_name_input)

        self.printer_interface_input = QLineEdit()
        layout.addRow("Printer Interface:", self.printer_interface_input)

        group.setLayout(layout)
        return group

    def load_settings(self):
        """Load settings from database"""
        # Business settings
        rice_price = ConfigService.get_float_value(
            self.db, 'rice_price_per_1000kg', 1500.00
        )
        self.rice_price_input.setValue(rice_price)

        subsidy_rate = ConfigService.get_float_value(
            self.db, 'subsidy_rate', 0.50
        )
        self.subsidy_rate_input.setValue(subsidy_rate)

        wap_basah = ConfigService.get_float_value(
            self.db, 'discount_wap_basah_default', 7.00
        )
        self.wap_basah_input.setValue(wap_basah)

        hampa_padi = ConfigService.get_float_value(
            self.db, 'discount_hampa_padi_default', 7.00
        )
        self.hampa_padi_input.setValue(hampa_padi)

        padi_muda = ConfigService.get_float_value(
            self.db, 'discount_padi_muda_default', 6.00
        )
        self.padi_muda_input.setValue(padi_muda)

        # Company info
        company_name = ConfigService.get_value(self.db, 'company_name', 'AYOP BIN ARSHAD')
        self.company_name_input.setText(company_name)

        company_addr1 = ConfigService.get_value(
            self.db, 'company_address',
            'LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR'
        )
        self.company_address1_input.setText(company_addr1)

        company_addr2 = ConfigService.get_value(
            self.db, 'company_address_2', 'SELANGOR DARUL EHSAN'
        )
        self.company_address2_input.setText(company_addr2)

        company_reg = ConfigService.get_value(self.db, 'company_registration', '474523-K')
        self.company_reg_input.setText(company_reg)

        company_phone = ConfigService.get_value(self.db, 'company_phone', '0162120051')
        self.company_phone_input.setText(company_phone)

        manager = ConfigService.get_value(self.db, 'manager_name', 'AH SENG')
        self.manager_name_input.setText(manager)

        # Printer settings
        self.printer_name_input.setText("EPSON LQ-310")
        self.printer_interface_input.setText("usb")

    def save_settings(self):
        """Save settings to database"""
        try:
            ConfigService.set_value(
                self.db, 'rice_price_per_1000kg',
                str(self.rice_price_input.value())
            )
            ConfigService.set_value(
                self.db, 'subsidy_rate',
                str(self.subsidy_rate_input.value())
            )
            ConfigService.set_value(
                self.db, 'discount_wap_basah_default',
                str(self.wap_basah_input.value())
            )
            ConfigService.set_value(
                self.db, 'discount_hampa_padi_default',
                str(self.hampa_padi_input.value())
            )
            ConfigService.set_value(
                self.db, 'discount_padi_muda_default',
                str(self.padi_muda_input.value())
            )
            ConfigService.set_value(
                self.db, 'company_name',
                self.company_name_input.text()
            )
            ConfigService.set_value(
                self.db, 'company_address',
                self.company_address1_input.text()
            )
            ConfigService.set_value(
                self.db, 'company_address_2',
                self.company_address2_input.text()
            )
            ConfigService.set_value(
                self.db, 'company_registration',
                self.company_reg_input.text()
            )
            ConfigService.set_value(
                self.db, 'company_phone',
                self.company_phone_input.text()
            )
            ConfigService.set_value(
                self.db, 'manager_name',
                self.manager_name_input.text()
            )

            QMessageBox.information(self, "Success", "Settings saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def reset_to_defaults(self):
        """Reset to default values"""
        reply = QMessageBox.question(
            self, "Confirm",
            "Reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Reset to default values
            self.rice_price_input.setValue(1500.00)
            self.subsidy_rate_input.setValue(0.50)
            self.wap_basah_input.setValue(7.00)
            self.hampa_padi_input.setValue(7.00)
            self.padi_muda_input.setValue(6.00)
            self.company_name_input.setText("AYOP BIN ARSHAD")
            self.company_address1_input.setText(
                "LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR"
            )
            self.company_address2_input.setText("SELANGOR DARUL EHSAN")
            self.company_reg_input.setText("474523-K")
            self.company_phone_input.setText("0162120051")
            self.manager_name_input.setText("AH SENG")
