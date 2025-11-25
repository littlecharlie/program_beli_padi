"""
Truck Selector Widget
Reusable widget for selecting trucks from dropdown
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QComboBox, QLabel, QDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from services.truck_service import TruckService
from config.database import get_db


class TruckSelectorWidget(QWidget):
    """Widget for selecting a truck"""

    # Signal emitted when truck is selected
    truck_selected = pyqtSignal(int, str)  # truck_id, truck_number

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db()
        self.selected_truck = None
        self.setup_ui()
        self.load_trucks()

    def setup_ui(self):
        """Setup user interface"""
        layout = QHBoxLayout()

        self.label = QLabel("Truck:")
        self.truck_combo = QComboBox()
        self.truck_combo.setMinimumWidth(200)
        self.add_truck_btn = QPushButton("Add New")

        layout.addWidget(self.label)
        layout.addWidget(self.truck_combo)
        layout.addWidget(self.add_truck_btn)
        layout.addStretch()

        self.setLayout(layout)

        # Connect signals
        self.truck_combo.currentIndexChanged.connect(self.on_truck_changed)
        self.add_truck_btn.clicked.connect(self.add_new_truck)

    def load_trucks(self):
        """Load all active trucks into combo box"""
        self.truck_combo.blockSignals(True)
        self.truck_combo.clear()

        trucks = TruckService.get_all(self.db, active_only=True)

        if not trucks:
            self.truck_combo.addItem("No trucks available", None)
            self.truck_combo.blockSignals(False)
            return

        for truck in trucks:
            display_text = truck.truck_number
            if truck.tare_weight:
                display_text += f" (Tare: {truck.tare_weight} kg)"
            self.truck_combo.addItem(display_text, truck.id)

        self.truck_combo.blockSignals(False)

        # Select first truck by default
        if self.truck_combo.count() > 0:
            self.on_truck_changed(0)

    def on_truck_changed(self, index):
        """Handle truck selection change"""
        truck_id = self.truck_combo.currentData()
        if truck_id:
            truck = TruckService.get_by_id(self.db, truck_id)
            if truck:
                self.selected_truck = truck
                self.truck_selected.emit(truck.id, truck.truck_number)

    def add_new_truck(self):
        """Open dialog to add new truck"""
        from ui.dialogs.truck_dialog import TruckDialog
        dialog = TruckDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # New truck created, refresh
            self.load_trucks()

    def get_selected_truck(self):
        """Get currently selected truck"""
        return self.selected_truck

    def get_selected_truck_id(self):
        """Get selected truck ID"""
        if self.selected_truck:
            return self.selected_truck.id
        return None

    def get_selected_truck_number(self):
        """Get selected truck number"""
        if self.selected_truck:
            return self.selected_truck.truck_number
        return None

    def set_truck(self, truck_id: int):
        """Set selected truck by ID"""
        for i in range(self.truck_combo.count()):
            if self.truck_combo.itemData(i) == truck_id:
                self.truck_combo.setCurrentIndex(i)
                return True
        return False
