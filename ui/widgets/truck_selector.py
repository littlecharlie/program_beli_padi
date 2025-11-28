"""
Truck Selector Widget
Reusable widget for selecting trucks from dropdown
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QComboBox, QLabel, QDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
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

        # Enhanced dropdown styling with visible icon
        self.truck_combo.setStyleSheet("""
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
        """)

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
        if dialog.exec() == QDialog.Accepted:
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
