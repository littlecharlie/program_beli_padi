"""
Farmer Selector Widget
Reusable widget for selecting farmers with search and auto-lookup
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QListWidget, QListWidgetItem,
    QDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from services.farmer_service import FarmerService
from config.database import get_db


class FarmerSelectorWidget(QWidget):
    """Widget for selecting a farmer"""

    # Signal emitted when farmer is selected
    farmer_selected = pyqtSignal(int, str, str)  # farmer_id, name, ic_number

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.selected_farmer = None
        self.setup_ui()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout()

        # IC Number input
        ic_layout = QHBoxLayout()
        self.ic_label = QLabel("Farmer IC:")
        self.ic_input = QLineEdit()
        self.ic_input.setPlaceholderText("Enter or scan IC number")
        self.search_btn = QPushButton("Search")
        self.add_farmer_btn = QPushButton("Add New")

        ic_layout.addWidget(self.ic_label)
        ic_layout.addWidget(self.ic_input)
        ic_layout.addWidget(self.search_btn)
        ic_layout.addWidget(self.add_farmer_btn)

        layout.addLayout(ic_layout)

        # Search results list
        self.results_label = QLabel("Search Results:")
        self.results_list = QListWidget()
        layout.addWidget(self.results_label)
        layout.addWidget(self.results_list)

        # Selected farmer display
        self.selected_label = QLabel("Selected Farmer: None")
        layout.addWidget(self.selected_label)

        self.setLayout(layout)

        # Connect signals
        self.search_btn.clicked.connect(self.search_farmers)
        self.add_farmer_btn.clicked.connect(self.add_new_farmer)
        self.results_list.itemClicked.connect(self.on_farmer_selected)
        self.ic_input.returnPressed.connect(self.search_farmers)

    def search_farmers(self):
        """Search for farmers by IC or name"""
        search_term = self.ic_input.text().strip()
        if not search_term:
            QMessageBox.warning(self, "Warning", "Please enter IC number or name")
            return

        self.results_list.clear()

        # Search for farmers
        farmers = FarmerService.search(self.db, search_term)

        if not farmers:
            QMessageBox.information(self, "No Results", "No farmers found matching your search")
            return

        # Display results
        for farmer in farmers:
            item_text = f"{farmer.name} (IC: {farmer.ic_number})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, farmer.id)
            self.results_list.addItem(item)

    def on_farmer_selected(self, item):
        """Handle farmer selection from list"""
        farmer_id = item.data(Qt.ItemDataRole.UserRole)
        farmer = FarmerService.get_by_id(self.db, farmer_id)

        if farmer:
            self.selected_farmer = farmer
            # Display farmer name followed by IC number
            self.ic_input.setText(f"{farmer.name} ({farmer.ic_number})")
            self.selected_label.setText(
                f"Selected: {farmer.name} (IC: {farmer.ic_number})"
            )
            self.results_list.clear()
            self.farmer_selected.emit(farmer.id, farmer.name, farmer.ic_number)

    def add_new_farmer(self):
        """Open dialog to add new farmer"""
        from ui.dialogs.farmer_dialog import FarmerDialog
        dialog = FarmerDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # New farmer created, refresh
            self.search_farmers()

    def get_selected_farmer(self):
        """Get currently selected farmer"""
        return self.selected_farmer

    def get_selected_farmer_id(self):
        """Get selected farmer ID"""
        if self.selected_farmer:
            return self.selected_farmer.id
        return None

    def clear_selection(self):
        """Clear current selection"""
        self.selected_farmer = None
        self.ic_input.clear()
        self.results_list.clear()
        self.selected_label.setText("Selected Farmer: None")
