"""
Main Application Window
PyQt6 main window for the Rice Billing System
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles import STYLESHEET
from config.database import get_db


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rice Billing System - AYOP BIN ARSHAD")
        self.setGeometry(100, 100, 1200, 800)

        # Apply stylesheet
        self.setStyleSheet(STYLESHEET)

        # Database session
        self.db = get_db()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Title
        title_label = QLabel("Rice Billing System")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Navigation buttons layout
        nav_layout = QHBoxLayout()

        self.dashboard_btn = QPushButton("Dashboard")
        self.purchase_btn = QPushButton("Purchase")
        self.delivery_btn = QPushButton("Delivery")
        self.farmers_btn = QPushButton("Farmers")
        self.mills_btn = QPushButton("Mills")
        self.trucks_btn = QPushButton("Trucks")
        self.reports_btn = QPushButton("Reports")
        self.settings_btn = QPushButton("Settings")

        nav_layout.addWidget(self.dashboard_btn)
        nav_layout.addWidget(self.purchase_btn)
        nav_layout.addWidget(self.delivery_btn)
        nav_layout.addWidget(self.farmers_btn)
        nav_layout.addWidget(self.mills_btn)
        nav_layout.addWidget(self.trucks_btn)
        nav_layout.addWidget(self.reports_btn)
        nav_layout.addWidget(self.settings_btn)
        nav_layout.addStretch()

        main_layout.addLayout(nav_layout)

        # Content area (stacked widget for screens)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Placeholder content
        placeholder = QLabel("Screen content will load here")
        self.stacked_widget.addWidget(placeholder)

        central_widget.setLayout(main_layout)

        # Connect button signals (to be implemented)
        self.setup_connections()

    def setup_connections(self):
        """Setup button signal connections"""
        self.dashboard_btn.clicked.connect(self.show_dashboard)
        self.purchase_btn.clicked.connect(self.show_purchase)
        self.delivery_btn.clicked.connect(self.show_delivery)
        self.farmers_btn.clicked.connect(self.show_farmers)
        self.mills_btn.clicked.connect(self.show_mills)
        self.trucks_btn.clicked.connect(self.show_trucks)
        self.reports_btn.clicked.connect(self.show_reports)
        self.settings_btn.clicked.connect(self.show_settings)

        # Initialize screens
        self._init_screens()

    def _init_screens(self):
        """Initialize all screens"""
        from ui.screens.purchase_entry import PurchaseEntryScreen
        from ui.screens.purchase_list import PurchaseListScreen
        from ui.screens.delivery_entry import DeliveryEntryScreen
        from ui.screens.delivery_list import DeliveryListScreen

        # Create screens
        self.purchase_entry_screen = PurchaseEntryScreen()
        self.purchase_list_screen = PurchaseListScreen()
        self.delivery_entry_screen = DeliveryEntryScreen()
        self.delivery_list_screen = DeliveryListScreen()

        # Add to stacked widget
        self.stacked_widget.addWidget(self.purchase_entry_screen)
        self.stacked_widget.addWidget(self.purchase_list_screen)
        self.stacked_widget.addWidget(self.delivery_entry_screen)
        self.stacked_widget.addWidget(self.delivery_list_screen)

    def show_dashboard(self):
        """Show dashboard screen"""
        QMessageBox.information(self, "Info", "Dashboard screen not yet implemented")

    def show_purchase(self):
        """Show purchase list screen"""
        self.stacked_widget.setCurrentWidget(self.purchase_list_screen)

    def show_delivery(self):
        """Show delivery invoice list screen"""
        self.stacked_widget.setCurrentWidget(self.delivery_list_screen)

    def show_farmers(self):
        """Show farmer management screen"""
        QMessageBox.information(self, "Info", "Farmer management screen not yet implemented")

    def show_mills(self):
        """Show rice mill management screen"""
        QMessageBox.information(self, "Info", "Rice mill management screen not yet implemented")

    def show_trucks(self):
        """Show truck management screen"""
        QMessageBox.information(self, "Info", "Truck management screen not yet implemented")

    def show_reports(self):
        """Show reports screen"""
        QMessageBox.information(self, "Info", "Reports screen not yet implemented")

    def show_settings(self):
        """Show settings screen"""
        QMessageBox.information(self, "Info", "Settings screen not yet implemented")

    def closeEvent(self, event):
        """Close database connection on exit"""
        if self.db:
            self.db.close()
        event.accept()
