"""
Dashboard Screen
Main dashboard showing key statistics and quick actions
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime, timedelta
from config.database import get_db
from services.purchase_service import PurchaseService
from services.delivery_service import DeliveryService
from services.farmer_service import FarmerService
from services.rice_mill_service import RiceMillService


class DashboardScreen(QWidget):
    """Main dashboard screen"""

    # Signals for navigation
    go_to_purchase = pyqtSignal()
    go_to_delivery = pyqtSignal()
    go_to_farmers = pyqtSignal()
    go_to_reports = pyqtSignal()

    def __init__(self, parent=None, demo_mode=False):
        super().__init__(parent)
        self.demo_mode = demo_mode
        self.db = None if demo_mode else get_db()
        # Store references to stat labels for updates
        self.stat_labels = {}
        self.setup_ui()
        if not demo_mode:
            self.load_statistics()

    def setup_ui(self):
        """Setup user interface"""
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        main_layout.addWidget(title)

        # Statistics Group
        stats_group = self._create_statistics_group()
        main_layout.addWidget(stats_group)

        # Today's Activity Group
        today_group = self._create_today_activity_group()
        main_layout.addWidget(today_group)

        # Quick Actions Group
        actions_group = self._create_quick_actions_group()
        main_layout.addWidget(actions_group)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def _create_statistics_group(self) -> QGroupBox:
        """Create statistics group"""
        group = QGroupBox("Overall Statistics")
        layout = QGridLayout()

        # Get statistics
        if self.demo_mode:
            # Demo data
            purchase_stats = {
                'total_bills': 45,
                'pending_bills': 12,
                'delivered_bills': 33,
                'total_weight': 5250,
                'delivered_weight': 4200,
                'total_payment': 78750.00,
                'delivered_payment': 63000.00
            }
            delivery_stats = {
                'total_invoices': 8,
                'total_bills_delivered': 33,
                'total_weight': 5250,
                'avg_invoice_weight': 656
            }
            farmer_count = 15
        else:
            purchase_stats = PurchaseService.get_statistics(self.db)
            delivery_stats = DeliveryService.get_statistics(self.db)
            farmer_count = FarmerService.count(self.db)

        # Column 1: Purchase Stats
        layout.addWidget(QLabel("PURCHASE BILLS"), 0, 0)
        layout.addWidget(self._create_stat_card(
            "Total Bills",
            str(purchase_stats['total_bills']),
            "#4da6ff",  # Brighter blue for dark mode
            "total_bills"
        ), 1, 0)
        layout.addWidget(self._create_stat_card(
            "Pending",
            str(purchase_stats['pending_bills']),
            "#ff9800",  # Brighter orange
            "pending_bills"
        ), 2, 0)
        layout.addWidget(self._create_stat_card(
            "Delivered",
            str(purchase_stats['delivered_bills']),
            "#4caf50",  # Brighter green
            "delivered_bills"
        ), 3, 0)

        # Column 2: Weight Stats
        layout.addWidget(QLabel("WEIGHT STATISTICS"), 0, 1)
        layout.addWidget(self._create_stat_card(
            f"Total Weight",
            f"{purchase_stats['total_weight']:,.0f} kg",
            "#29b6f6",  # Brighter cyan
            "total_weight"
        ), 1, 1)
        layout.addWidget(self._create_stat_card(
            f"Pending Weight",
            f"{purchase_stats['total_weight'] - purchase_stats['delivered_weight']:,.0f} kg",
            "#ffb74d",  # Lighter orange
            "pending_weight"
        ), 2, 1)
        layout.addWidget(self._create_stat_card(
            f"Delivered Weight",
            f"{purchase_stats['delivered_weight']:,.0f} kg",
            "#4caf50",  # Brighter green
            "delivered_weight"
        ), 3, 1)

        # Column 3: Payment Stats
        layout.addWidget(QLabel("PAYMENT INFORMATION"), 0, 2)
        layout.addWidget(self._create_stat_card(
            "Total Payment",
            f"RM {purchase_stats['total_payment']:,.2f}",
            "#4da6ff",  # Brighter blue
            "total_payment"
        ), 1, 2)
        layout.addWidget(self._create_stat_card(
            "Pending Payment",
            f"RM {purchase_stats['total_payment'] - purchase_stats['delivered_payment']:,.2f}",
            "#ff9800",  # Brighter orange
            "pending_payment"
        ), 2, 2)
        layout.addWidget(self._create_stat_card(
            "Paid Payment",
            f"RM {purchase_stats['delivered_payment']:,.2f}",
            "#4caf50",  # Brighter green
            "paid_payment"
        ), 3, 2)

        # Column 4: Delivery Stats
        layout.addWidget(QLabel("DELIVERY INVOICES"), 0, 3)
        layout.addWidget(self._create_stat_card(
            "Total Invoices",
            str(delivery_stats['total_invoices']),
            "#ab47bc",  # Brighter purple
            "total_invoices"
        ), 1, 3)
        layout.addWidget(self._create_stat_card(
            "Bills Delivered",
            str(delivery_stats['total_bills_delivered']),
            "#4caf50",  # Brighter green
            "bills_delivered"
        ), 2, 3)
        layout.addWidget(self._create_stat_card(
            "Avg Weight",
            f"{delivery_stats['avg_invoice_weight']:,.0f} kg",
            "#29b6f6",  # Brighter cyan
            "avg_invoice_weight"
        ), 3, 3)

        # Store stats for later updates
        self.purchase_stats = purchase_stats
        self.delivery_stats = delivery_stats

        group.setLayout(layout)
        return group

    def _create_today_activity_group(self) -> QGroupBox:
        """Create today's activity group"""
        group = QGroupBox("Today's Activity")
        layout = QGridLayout()

        # Get today's data
        if self.demo_mode:
            # Demo data
            today_bills_count = 3
            today_invoices_count = 1
            today_weight = 450
            today_payment = 6750.00
            today_delivered_weight = 380
        else:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())

            today_bills = PurchaseService.get_by_date_range(self.db, today_start, today_end)
            today_invoices = DeliveryService.get_by_date_range(self.db, today_start, today_end)

            today_bills_count = len(today_bills)
            today_invoices_count = len(today_invoices)
            today_weight = sum(float(b.net_weight) for b in today_bills)
            today_payment = sum(float(b.total_payment) for b in today_bills)
            today_delivered_weight = sum(float(i.total_weight) for i in today_invoices)

        # Activity cards
        layout.addWidget(self._create_stat_card(
            "New Bills",
            str(today_bills_count),
            "#4da6ff",  # Brighter blue
            "today_bills"
        ), 0, 0)
        layout.addWidget(self._create_stat_card(
            "New Deliveries",
            str(today_invoices_count),
            "#4caf50",  # Brighter green
            "today_invoices"
        ), 0, 1)
        layout.addWidget(self._create_stat_card(
            "Today's Weight",
            f"{today_weight:,.0f} kg",
            "#29b6f6",  # Brighter cyan
            "today_weight"
        ), 0, 2)
        layout.addWidget(self._create_stat_card(
            "Today's Payment",
            f"RM {today_payment:,.2f}",
            "#ff9800",  # Brighter orange
            "today_payment"
        ), 0, 3)
        layout.addWidget(self._create_stat_card(
            "Delivered Today",
            f"{today_delivered_weight:,.0f} kg",
            "#ab47bc",  # Brighter purple
            "today_delivered_weight"
        ), 0, 4)

        # Store today's stats
        self.today_data = {
            'bills': today_bills_count,
            'invoices': today_invoices_count,
            'weight': today_weight,
            'payment': today_payment,
            'delivered_weight': today_delivered_weight
        }

        layout.setColumnStretch(5, 1)
        group.setLayout(layout)
        return group

    def _create_quick_actions_group(self) -> QGroupBox:
        """Create quick actions group"""
        group = QGroupBox("Quick Actions")
        layout = QHBoxLayout()

        # Buttons with dark mode optimized colors
        new_purchase_btn = QPushButton("New Purchase Bill")
        new_purchase_btn.setStyleSheet("""
            background-color: #4da6ff;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11pt;
        """)
        new_purchase_btn.setMinimumHeight(50)
        new_purchase_btn.clicked.connect(self.go_to_purchase.emit)

        new_delivery_btn = QPushButton("Create Delivery")
        new_delivery_btn.setStyleSheet("""
            background-color: #4caf50;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11pt;
        """)
        new_delivery_btn.setMinimumHeight(50)
        new_delivery_btn.clicked.connect(self.go_to_delivery.emit)

        view_farmers_btn = QPushButton("Manage Farmers")
        view_farmers_btn.setStyleSheet("""
            background-color: #ab47bc;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11pt;
        """)
        view_farmers_btn.setMinimumHeight(50)
        view_farmers_btn.clicked.connect(self.go_to_farmers.emit)

        reports_btn = QPushButton("View Reports")
        reports_btn.setStyleSheet("""
            background-color: #ff9800;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11pt;
        """)
        reports_btn.setMinimumHeight(50)
        reports_btn.clicked.connect(self.go_to_reports.emit)

        layout.addWidget(new_purchase_btn)
        layout.addWidget(new_delivery_btn)
        layout.addWidget(view_farmers_btn)
        layout.addWidget(reports_btn)
        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_stat_card(self, title: str, value: str, color: str, label_key: str = None) -> QGroupBox:
        """Create a statistics card"""
        card = QGroupBox(title)
        layout = QVBoxLayout()

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignCenter)

        # Store reference if label_key provided
        if label_key:
            self.stat_labels[label_key] = (value_label, color)

        layout.addWidget(value_label)
        card.setLayout(layout)
        card.setMaximumHeight(100)

        return card

    def load_statistics(self):
        """Load and refresh statistics"""
        # This is called on setup and can be called again to refresh
        pass

    def refresh(self):
        """Refresh all statistics without recreating UI"""
        if self.demo_mode:
            return

        # Fetch fresh data
        purchase_stats = PurchaseService.get_statistics(self.db)
        delivery_stats = DeliveryService.get_statistics(self.db)

        # Update stored stats
        self.purchase_stats = purchase_stats
        self.delivery_stats = delivery_stats

        # Update stat labels
        if 'total_bills' in self.stat_labels:
            label, color = self.stat_labels['total_bills']
            label.setText(str(purchase_stats['total_bills']))

        if 'pending_bills' in self.stat_labels:
            label, color = self.stat_labels['pending_bills']
            label.setText(str(purchase_stats['pending_bills']))

        if 'delivered_bills' in self.stat_labels:
            label, color = self.stat_labels['delivered_bills']
            label.setText(str(purchase_stats['delivered_bills']))

        if 'total_weight' in self.stat_labels:
            label, color = self.stat_labels['total_weight']
            label.setText(f"{purchase_stats['total_weight']:,.0f} kg")

        if 'pending_weight' in self.stat_labels:
            label, color = self.stat_labels['pending_weight']
            pending = purchase_stats['total_weight'] - purchase_stats['delivered_weight']
            label.setText(f"{pending:,.0f} kg")

        if 'delivered_weight' in self.stat_labels:
            label, color = self.stat_labels['delivered_weight']
            label.setText(f"{purchase_stats['delivered_weight']:,.0f} kg")

        if 'total_payment' in self.stat_labels:
            label, color = self.stat_labels['total_payment']
            label.setText(f"RM {purchase_stats['total_payment']:,.2f}")

        if 'pending_payment' in self.stat_labels:
            label, color = self.stat_labels['pending_payment']
            pending = purchase_stats['total_payment'] - purchase_stats['delivered_payment']
            label.setText(f"RM {pending:,.2f}")

        if 'paid_payment' in self.stat_labels:
            label, color = self.stat_labels['paid_payment']
            label.setText(f"RM {purchase_stats['delivered_payment']:,.2f}")

        if 'total_invoices' in self.stat_labels:
            label, color = self.stat_labels['total_invoices']
            label.setText(str(delivery_stats['total_invoices']))

        if 'bills_delivered' in self.stat_labels:
            label, color = self.stat_labels['bills_delivered']
            label.setText(str(delivery_stats['total_bills_delivered']))

        if 'avg_invoice_weight' in self.stat_labels:
            label, color = self.stat_labels['avg_invoice_weight']
            label.setText(f"{delivery_stats['avg_invoice_weight']:,.0f} kg")

        # Update today's activity
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        today_bills = PurchaseService.get_by_date_range(self.db, today_start, today_end)
        today_invoices = DeliveryService.get_by_date_range(self.db, today_start, today_end)

        today_bills_count = len(today_bills)
        today_invoices_count = len(today_invoices)
        today_weight = sum(float(b.net_weight) for b in today_bills)
        today_payment = sum(float(b.total_payment) for b in today_bills)
        today_delivered_weight = sum(float(i.total_weight) for i in today_invoices)

        if 'today_bills' in self.stat_labels:
            label, color = self.stat_labels['today_bills']
            label.setText(str(today_bills_count))

        if 'today_invoices' in self.stat_labels:
            label, color = self.stat_labels['today_invoices']
            label.setText(str(today_invoices_count))

        if 'today_weight' in self.stat_labels:
            label, color = self.stat_labels['today_weight']
            label.setText(f"{today_weight:,.0f} kg")

        if 'today_payment' in self.stat_labels:
            label, color = self.stat_labels['today_payment']
            label.setText(f"RM {today_payment:,.2f}")

        if 'today_delivered_weight' in self.stat_labels:
            label, color = self.stat_labels['today_delivered_weight']
            label.setText(f"{today_delivered_weight:,.0f} kg")
