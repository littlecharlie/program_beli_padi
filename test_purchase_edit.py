"""
Test Purchase Edit Functionality
Quick test to verify purchase bill editing works correctly
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from config.database import get_db
from services.purchase_service import PurchaseService
from ui.dialogs.purchase_edit_dialog import PurchaseEditDialog


class TestWindow(QMainWindow):
    """Test window for purchase edit dialog"""

    def __init__(self):
        super().__init__()
        self.db = get_db()
        self.setWindowTitle("Test Purchase Edit Dialog")
        self.setGeometry(100, 100, 400, 300)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Get a sample bill (first pending bill)
        pending_bills = PurchaseService.get_undelivered(self.db)

        if not pending_bills:
            from PyQt5.QtWidgets import QLabel
            label = QLabel("No pending bills found in database.\nPlease create a purchase bill first.")
            label.setStyleSheet("padding: 20px; font-size: 12px;")
            layout.addWidget(label)
        else:
            from PyQt5.QtWidgets import QLabel
            info = QLabel(f"Found {len(pending_bills)} pending bill(s).\nClick button to edit the first one:")
            info.setStyleSheet("padding: 10px; font-size: 11px;")
            layout.addWidget(info)

            # Display bill info
            first_bill = pending_bills[0]
            bill_info = QLabel(
                f"Bill Number: {first_bill.bill_number}\n"
                f"Farmer: {first_bill.farmer.name if first_bill.farmer else 'Unknown'}\n"
                f"Net Weight: {float(first_bill.net_weight):,.2f} kg\n"
                f"Total Payment: RM {float(first_bill.total_payment):,.2f}"
            )
            bill_info.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
            layout.addWidget(bill_info)

            # Test button
            test_btn = QPushButton(f"Edit Bill {first_bill.bill_number}")
            test_btn.setStyleSheet("padding: 10px; font-size: 12px; background-color: #007ACC; color: white;")
            test_btn.clicked.connect(lambda: self.test_edit_dialog(first_bill.id))
            layout.addWidget(test_btn)

        layout.addStretch()

    def test_edit_dialog(self, bill_id: int):
        """Open edit dialog for testing"""
        dialog = PurchaseEditDialog(bill_id=bill_id, parent=self)
        result = dialog.exec()

        if result == QDialog.Accepted:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Test Result",
                "Edit dialog completed successfully!\nChanges have been saved to the database."
            )
            # Refresh the display
            self.refresh_display()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Test Result",
                "Edit dialog was cancelled. No changes were made."
            )

    def refresh_display(self):
        """Refresh the window display"""
        self.close()
        new_window = TestWindow()
        new_window.show()


def main():
    """Run test"""
    app = QApplication(sys.argv)

    # Apply dark theme stylesheet
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
        }
    """)

    window = TestWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
