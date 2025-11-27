"""
Main Application Window
PyQt6 main window for the Rice Billing System
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.styles import STYLESHEET
from config.database import get_db


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, demo_mode=False):
        super().__init__()
        self.setWindowTitle("Rice Billing System - AYOP BIN ARSHAD")

        # Set responsive window size based on screen resolution
        self._set_responsive_window_size()

        self.demo_mode = demo_mode

        # Apply stylesheet
        self.setStyleSheet(STYLESHEET)

        # Database session (None in demo mode)
        self.db = None if demo_mode else get_db()

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

    def _set_responsive_window_size(self):
        """
        Set window size responsively based on screen resolution.
        Default target: 1280x720
        """
        # Get the primary screen
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()

            # Desired window dimensions
            window_width = 1280
            window_height = 720

            # Calculate if we need to scale down for smaller screens
            # Leave some margin (90% of screen size max)
            max_width = int(screen_width * 0.9)
            max_height = int(screen_height * 0.9)

            # Scale down if necessary while maintaining aspect ratio
            if window_width > max_width or window_height > max_height:
                # Calculate scale factor to fit within screen
                scale_width = max_width / window_width
                scale_height = max_height / window_height
                scale_factor = min(scale_width, scale_height)

                window_width = int(window_width * scale_factor)
                window_height = int(window_height * scale_factor)

            # Center the window on screen
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            # Set geometry (x, y, width, height)
            self.setGeometry(x, y, window_width, window_height)

            # Set minimum size to ensure usability (minimum 800x600)
            self.setMinimumSize(800, 600)

            # Make window resizable
            # Users can resize as needed, or maximize
            # Note: Window is resizable by default in PyQt5

            # Optional: Maximize window on very small screens (< 1366x768)
            if screen_width < 1366 or screen_height < 768:
                self.showMaximized()
        else:
            # Fallback if screen detection fails
            self.setGeometry(100, 100, 1280, 720)
            self.setMinimumSize(800, 600)

    def setup_connections(self):
        """Setup button signal connections"""
        self.dashboard_btn.clicked.connect(self.show_dashboard)
        self.purchase_btn.clicked.connect(self.show_purchase_list)
        self.delivery_btn.clicked.connect(self.show_delivery_list)
        self.farmers_btn.clicked.connect(self.show_farmers)
        self.mills_btn.clicked.connect(self.show_mills)
        self.trucks_btn.clicked.connect(self.show_trucks)
        self.reports_btn.clicked.connect(self.show_reports)
        self.settings_btn.clicked.connect(self.show_settings)

        # Initialize screens
        self._init_screens()

    def _init_screens(self):
        """Initialize all screens"""
        from ui.screens.dashboard import DashboardScreen

        # Create dashboard screen
        self.dashboard_screen = DashboardScreen(demo_mode=self.demo_mode)

        # Only create other screens if not in demo mode
        if not self.demo_mode:
            from ui.screens.purchase_entry import PurchaseEntryScreen
            from ui.screens.purchase_list import PurchaseListScreen
            from ui.screens.delivery_entry import DeliveryEntryScreen
            from ui.screens.delivery_list import DeliveryListScreen
            from ui.screens.reports import ReportsScreen
            from ui.screens.master_data import (
                FarmerManagementScreen,
                RiceMillManagementScreen,
                TruckManagementScreen
            )
            from ui.screens.settings import SettingsScreen

            self.purchase_entry_screen = PurchaseEntryScreen()
            self.purchase_list_screen = PurchaseListScreen()
            self.delivery_entry_screen = DeliveryEntryScreen()
            self.delivery_list_screen = DeliveryListScreen()
            self.farmer_management_screen = FarmerManagementScreen()
            self.mill_management_screen = RiceMillManagementScreen()
            self.truck_management_screen = TruckManagementScreen()
            self.reports_screen = ReportsScreen()
            self.settings_screen = SettingsScreen()
        else:
            # Create placeholder screens for demo mode
            self.purchase_entry_screen = QWidget()
            self.purchase_list_screen = QWidget()
            self.delivery_entry_screen = QWidget()
            self.delivery_list_screen = QWidget()
            self.farmer_management_screen = QWidget()
            self.mill_management_screen = QWidget()
            self.truck_management_screen = QWidget()
            self.reports_screen = QWidget()
            self.settings_screen = QWidget()

        # Add to stacked widget
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.purchase_entry_screen)
        self.stacked_widget.addWidget(self.purchase_list_screen)
        self.stacked_widget.addWidget(self.delivery_entry_screen)
        self.stacked_widget.addWidget(self.delivery_list_screen)
        self.stacked_widget.addWidget(self.farmer_management_screen)
        self.stacked_widget.addWidget(self.mill_management_screen)
        self.stacked_widget.addWidget(self.truck_management_screen)
        self.stacked_widget.addWidget(self.reports_screen)
        self.stacked_widget.addWidget(self.settings_screen)

        # Connect dashboard quick action signals
        self.dashboard_screen.go_to_purchase.connect(self.show_purchase_entry)
        self.dashboard_screen.go_to_delivery.connect(self.show_delivery_entry)
        self.dashboard_screen.go_to_farmers.connect(self.show_farmers)
        self.dashboard_screen.go_to_reports.connect(self.show_reports)

        # Connect list screen signals to entry screens (if not demo mode)
        if not self.demo_mode:
            # Purchase list screen connections
            self.purchase_list_screen.create_purchase_bill.connect(self.show_purchase_entry)

            # Delivery list screen connections
            self.delivery_list_screen.create_delivery_invoice.connect(self.show_delivery_entry)

            # Entry screen connections - when saved/created, return to list and refresh
            self.purchase_entry_screen.bill_saved.connect(self._on_purchase_bill_saved)
            self.delivery_entry_screen.invoice_created.connect(self._on_delivery_invoice_created)

    def _on_purchase_bill_saved(self, bill_id: int):
        """Handle purchase bill saved - return to list and refresh"""
        # Refresh the list
        if hasattr(self.purchase_list_screen, 'refresh'):
            self.purchase_list_screen.refresh()
        # Show the list screen
        self.show_purchase_list()
        # Optionally show success message
        QMessageBox.information(
            self,
            "Success",
            f"Purchase bill saved successfully! (ID: {bill_id})"
        )

    def _on_delivery_invoice_created(self, invoice_id: int):
        """Handle delivery invoice created - return to list and refresh"""
        # Refresh the list
        if hasattr(self.delivery_list_screen, 'refresh'):
            self.delivery_list_screen.refresh()
        # Show the list screen
        self.show_delivery_list()
        # Optionally show success message
        QMessageBox.information(
            self,
            "Success",
            f"Delivery invoice created successfully! (ID: {invoice_id})"
        )

    def show_dashboard(self):
        """Show dashboard screen"""
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)
        # Refresh dashboard statistics
        if hasattr(self.dashboard_screen, 'refresh'):
            self.dashboard_screen.refresh()

    def show_purchase_list(self):
        """Show purchase list screen"""
        self.stacked_widget.setCurrentWidget(self.purchase_list_screen)
        # Refresh the list when showing
        if hasattr(self.purchase_list_screen, 'refresh'):
            self.purchase_list_screen.refresh()

    def show_purchase_entry(self):
        """Show purchase entry screen"""
        self.stacked_widget.setCurrentWidget(self.purchase_entry_screen)
        # Reset the form for new entry
        if hasattr(self.purchase_entry_screen, 'reset_form'):
            self.purchase_entry_screen.reset_form()

    def show_delivery_list(self):
        """Show delivery invoice list screen"""
        self.stacked_widget.setCurrentWidget(self.delivery_list_screen)
        # Refresh the list when showing
        if hasattr(self.delivery_list_screen, 'refresh'):
            self.delivery_list_screen.refresh()

    def show_delivery_entry(self):
        """Show delivery entry screen"""
        self.stacked_widget.setCurrentWidget(self.delivery_entry_screen)
        # Reset the form for new entry
        if hasattr(self.delivery_entry_screen, 'reset_form'):
            self.delivery_entry_screen.reset_form()

    def show_farmers(self):
        """Show farmer management screen"""
        self.stacked_widget.setCurrentWidget(self.farmer_management_screen)

    def show_mills(self):
        """Show rice mill management screen"""
        self.stacked_widget.setCurrentWidget(self.mill_management_screen)

    def show_trucks(self):
        """Show truck management screen"""
        self.stacked_widget.setCurrentWidget(self.truck_management_screen)

    def show_reports(self):
        """Show reports screen"""
        self.stacked_widget.setCurrentWidget(self.reports_screen)

    def show_settings(self):
        """Show settings screen"""
        self.stacked_widget.setCurrentWidget(self.settings_screen)

    def closeEvent(self, event):
        """Close database connection on exit"""
        if self.db:
            self.db.close()
        event.accept()
