"""
Master Data Management Screens
Generic CRUD screens for farmers, rice mills, and trucks
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QDialog, QFormLayout, QDialogButtonBox, QSpinBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from config.database import get_db
from services.farmer_service import FarmerService
from services.rice_mill_service import RiceMillService
from services.truck_service import TruckService
from utils.validators import Validators


class FarmerManagementScreen(QWidget):
    """Screen for managing farmers"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.setup_ui()
        self.load_farmers()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Farmer Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Search/Action Group
        action_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by IC or name")
        self.search_input.returnPressed.connect(self.search)
        action_layout.addWidget(self.search_input)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        action_layout.addWidget(search_btn)

        add_btn = QPushButton("Add New Farmer")
        add_btn.setStyleSheet("background-color: #28a745; color: white;")
        add_btn.clicked.connect(self.add_farmer)
        action_layout.addWidget(add_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_farmers)
        action_layout.addWidget(refresh_btn)

        main_layout.addLayout(action_layout)

        # Farmers Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "IC Number",
            "Name",
            "Phone",
            "Registration No",
            "Status",
            "Edit",
            "Delete"
        ])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 80)
        # Disable cell editing - users must use the Edit button
        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

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

    def load_farmers(self):
        """Load all farmers"""
        farmers = FarmerService.get_all(self.db, active_only=False)
        self.populate_table(farmers)

    def populate_table(self, farmers):
        """Populate table with farmers"""
        self.table.setRowCount(len(farmers))

        for row, farmer in enumerate(farmers):
            # Set row height for consistent button sizing
            self.table.setRowHeight(row, 44)

            self.table.setItem(row, 0, QTableWidgetItem(farmer.ic_number))
            self.table.setItem(row, 1, QTableWidgetItem(farmer.name))
            self.table.setItem(row, 2, QTableWidgetItem(farmer.phone or ""))
            self.table.setItem(row, 3, QTableWidgetItem(farmer.registration_number or ""))

            status = "Active" if farmer.is_active else "Inactive"
            self.table.setItem(row, 4, QTableWidgetItem(status))

            # Create properly sized buttons
            edit_btn = self._create_table_button("Edit")
            edit_btn.clicked.connect(lambda checked, f_id=farmer.id: self.edit_farmer(f_id))
            self.table.setCellWidget(row, 5, edit_btn)

            # Red delete button
            delete_btn = self._create_table_button("Delete", """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            delete_btn.clicked.connect(lambda checked, f_id=farmer.id: self.delete_farmer(f_id))
            self.table.setCellWidget(row, 6, delete_btn)

    def search(self):
        """Search farmers"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_farmers()
            return

        farmers = FarmerService.search(self.db, search_term, active_only=False)
        self.populate_table(farmers)

    def add_farmer(self):
        """Add new farmer"""
        dialog = FarmerDialog(self.db, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_farmers()

    def edit_farmer(self, farmer_id: int):
        """Edit farmer"""
        farmer = FarmerService.get_by_id(self.db, farmer_id)
        if farmer:
            dialog = FarmerDialog(self.db, farmer, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.load_farmers()

    def delete_farmer(self, farmer_id: int):
        """Delete farmer"""
        farmer = FarmerService.get_by_id(self.db, farmer_id)
        if not farmer:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete farmer {farmer.name}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if FarmerService.delete(self.db, farmer_id):
                QMessageBox.information(self, "Success", "Farmer deleted")
                self.load_farmers()


class FarmerDialog(QDialog):
    """Dialog for adding/editing farmers"""

    def __init__(self, db, farmer=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.farmer = farmer
        self.setWindowTitle("Farmer" if not farmer else "Edit Farmer")
        self.setGeometry(100, 100, 400, 300)
        self.setup_ui()

    def setup_ui(self):
        """Setup form"""
        layout = QFormLayout()

        self.ic_input = QLineEdit()
        self.ic_input.setReadOnly(bool(self.farmer))
        layout.addRow("IC Number:", self.ic_input)

        self.name_input = QLineEdit()
        layout.addRow("Name:", self.name_input)

        self.phone_input = QLineEdit()
        layout.addRow("Phone:", self.phone_input)

        self.reg_input = QLineEdit()
        layout.addRow("Registration No:", self.reg_input)

        self.subsidy_input = QLineEdit()
        layout.addRow("Subsidy Code:", self.subsidy_input)

        self.address_input = QLineEdit()
        layout.addRow("Address:", self.address_input)

        self.bank_input = QLineEdit()
        layout.addRow("Bank Account:", self.bank_input)

        if self.farmer:
            self.ic_input.setText(self.farmer.ic_number)
            self.name_input.setText(self.farmer.name)
            self.phone_input.setText(self.farmer.phone or "")
            self.reg_input.setText(self.farmer.registration_number or "")
            self.subsidy_input.setText(self.farmer.subsidy_code or "")
            self.address_input.setText(self.farmer.address or "")
            self.bank_input.setText(self.farmer.bank_account or "")

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def accept(self):
        """Save farmer"""
        ic = self.ic_input.text().strip()
        name = self.name_input.text().strip()

        if not ic or not name:
            QMessageBox.warning(self, "Error", "IC and Name are required")
            return

        is_valid, error = Validators.validate_ic_number(ic)
        if not is_valid:
            QMessageBox.warning(self, "Error", error)
            return

        try:
            if self.farmer:
                FarmerService.update(
                    self.db,
                    self.farmer.id,
                    name=name,
                    phone=self.phone_input.text() or None,
                    registration_number=self.reg_input.text() or None,
                    subsidy_code=self.subsidy_input.text() or None,
                    address=self.address_input.text() or None,
                    bank_account=self.bank_input.text() or None
                )
            else:
                FarmerService.create(
                    self.db,
                    ic_number=ic,
                    name=name,
                    phone=self.phone_input.text() or None,
                    registration_number=self.reg_input.text() or None,
                    subsidy_code=self.subsidy_input.text() or None,
                    address=self.address_input.text() or None,
                    bank_account=self.bank_input.text() or None
                )

            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")


class RiceMillManagementScreen(QWidget):
    """Screen for managing rice mills"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.setup_ui()
        self.load_mills()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        title = QLabel("Rice Mill Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        action_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by code or name")
        self.search_input.returnPressed.connect(self.search)
        action_layout.addWidget(self.search_input)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        action_layout.addWidget(search_btn)

        add_btn = QPushButton("Add New Mill")
        add_btn.setStyleSheet("background-color: #28a745; color: white;")
        add_btn.clicked.connect(self.add_mill)
        action_layout.addWidget(add_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_mills)
        action_layout.addWidget(refresh_btn)

        main_layout.addLayout(action_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Code",
            "Name",
            "Phone",
            "Status",
            "Edit",
            "Delete"
        ])
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 80)
        # Disable cell editing - users must use the Edit button
        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

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
        """Load all mills"""
        mills = RiceMillService.get_all(self.db, active_only=False)
        self.populate_table(mills)

    def populate_table(self, mills):
        """Populate table"""
        self.table.setRowCount(len(mills))

        for row, mill in enumerate(mills):
            # Set row height for consistent button sizing
            self.table.setRowHeight(row, 44)

            self.table.setItem(row, 0, QTableWidgetItem(mill.mill_code))
            self.table.setItem(row, 1, QTableWidgetItem(mill.mill_name))
            self.table.setItem(row, 2, QTableWidgetItem(mill.phone or ""))

            status = "Active" if mill.is_active else "Inactive"
            self.table.setItem(row, 3, QTableWidgetItem(status))

            # Create properly sized buttons
            edit_btn = self._create_table_button("Edit")
            edit_btn.clicked.connect(lambda checked, m_id=mill.id: self.edit_mill(m_id))
            self.table.setCellWidget(row, 4, edit_btn)

            # Red delete button
            delete_btn = self._create_table_button("Delete", """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            delete_btn.clicked.connect(lambda checked, m_id=mill.id: self.delete_mill(m_id))
            self.table.setCellWidget(row, 5, delete_btn)

    def search(self):
        """Search mills"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_mills()
            return

        mills = RiceMillService.search(self.db, search_term, active_only=False)
        self.populate_table(mills)

    def add_mill(self):
        """Add new mill"""
        QMessageBox.information(self, "Info", "Mill dialog not yet implemented")

    def edit_mill(self, mill_id: int):
        """Edit mill"""
        QMessageBox.information(self, "Info", "Mill edit dialog not yet implemented")

    def delete_mill(self, mill_id: int):
        """Delete mill"""
        mill = RiceMillService.get_by_id(self.db, mill_id)
        if mill:
            reply = QMessageBox.question(
                self, "Confirm",
                f"Delete {mill.mill_name}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if RiceMillService.delete(self.db, mill_id):
                    QMessageBox.information(self, "Success", "Mill deleted")
                    self.load_mills()


class TruckManagementScreen(QWidget):
    """Screen for managing trucks"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.setup_ui()
        self.load_trucks()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        title = QLabel("Truck Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        action_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by truck number")
        self.search_input.returnPressed.connect(self.search)
        action_layout.addWidget(self.search_input)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        action_layout.addWidget(search_btn)

        add_btn = QPushButton("Add New Truck")
        add_btn.setStyleSheet("background-color: #28a745; color: white;")
        add_btn.clicked.connect(self.add_truck)
        action_layout.addWidget(add_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_trucks)
        action_layout.addWidget(refresh_btn)

        main_layout.addLayout(action_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Truck Number",
            "Tare Weight",
            "Status",
            "Edit",
            "Delete"
        ])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        # Disable cell editing - users must use the Edit button
        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        main_layout.addWidget(self.table)
        self.setLayout(main_layout)

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

    def load_trucks(self):
        """Load all trucks"""
        trucks = TruckService.get_all(self.db, active_only=False)
        self.populate_table(trucks)

    def populate_table(self, trucks):
        """Populate table"""
        self.table.setRowCount(len(trucks))

        for row, truck in enumerate(trucks):
            # Set row height for consistent button sizing
            self.table.setRowHeight(row, 44)

            self.table.setItem(row, 0, QTableWidgetItem(truck.truck_number))

            tare = f"{float(truck.tare_weight):.2f}" if truck.tare_weight else "0"
            self.table.setItem(row, 1, QTableWidgetItem(tare))

            status = "Active" if truck.is_active else "Inactive"
            self.table.setItem(row, 2, QTableWidgetItem(status))

            # Create properly sized buttons
            edit_btn = self._create_table_button("Edit")
            edit_btn.clicked.connect(lambda checked, t_id=truck.id: self.edit_truck(t_id))
            self.table.setCellWidget(row, 3, edit_btn)

            # Red delete button
            delete_btn = self._create_table_button("Delete", """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)
            delete_btn.clicked.connect(lambda checked, t_id=truck.id: self.delete_truck(t_id))
            self.table.setCellWidget(row, 4, delete_btn)

    def search(self):
        """Search trucks"""
        search_term = self.search_input.text().strip()
        if not search_term:
            self.load_trucks()
            return

        trucks = TruckService.search(self.db, search_term, active_only=False)
        self.populate_table(trucks)

    def add_truck(self):
        """Add new truck"""
        QMessageBox.information(self, "Info", "Truck dialog not yet implemented")

    def edit_truck(self, truck_id: int):
        """Edit truck"""
        QMessageBox.information(self, "Info", "Truck edit dialog not yet implemented")

    def delete_truck(self, truck_id: int):
        """Delete truck"""
        truck = TruckService.get_by_id(self.db, truck_id)
        if truck:
            reply = QMessageBox.question(
                self, "Confirm",
                f"Delete truck {truck.truck_number}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if TruckService.delete(self.db, truck_id):
                    QMessageBox.information(self, "Success", "Truck deleted")
                    self.load_trucks()
