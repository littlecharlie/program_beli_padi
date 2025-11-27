"""
Export Helper Functions
Utilities for PDF export operations, notifications, and file handling
"""
from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtCore import QTimer
import subprocess
import platform
from pathlib import Path
from typing import Tuple


class ExportNotification:
    """Helper class for export notifications"""

    @staticmethod
    def show_success(parent: QWidget, file_path: str, item_count: int = 1):
        """
        Show success notification

        Args:
            parent: Parent widget
            file_path: Path to exported file
            item_count: Number of items exported
        """
        item_text = "item" if item_count == 1 else "items"
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Export Successful")
        msg.setText(f"Successfully exported {item_count} {item_text} to PDF")
        msg.setInformativeText(f"File saved to:\n{file_path}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    @staticmethod
    def show_error(parent: QWidget, error_message: str):
        """
        Show error notification

        Args:
            parent: Parent widget
            error_message: Error message to display
        """
        QMessageBox.critical(
            parent,
            "Export Failed",
            f"Failed to export PDF:\n\n{error_message}"
        )

    @staticmethod
    def show_warning(parent: QWidget, warning_message: str):
        """
        Show warning notification

        Args:
            parent: Parent widget
            warning_message: Warning message to display
        """
        QMessageBox.warning(
            parent,
            "Export Warning",
            warning_message
        )

    @staticmethod
    def show_info(parent: QWidget, title: str, message: str):
        """
        Show info notification

        Args:
            parent: Parent widget
            title: Dialog title
            message: Info message
        """
        QMessageBox.information(parent, title, message)

    @staticmethod
    def confirm_overwrite(parent: QWidget, file_path: str) -> bool:
        """
        Ask user to confirm file overwrite

        Args:
            parent: Parent widget
            file_path: Path to file that would be overwritten

        Returns:
            True if user confirms, False otherwise
        """
        reply = QMessageBox.question(
            parent,
            "File Exists",
            f"The file already exists:\n{file_path}\n\nDo you want to overwrite it?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes


class FileOperations:
    """Helper class for file operations"""

    @staticmethod
    def open_file(file_path: str) -> bool:
        """
        Open file with system default application

        Args:
            file_path: Path to file

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False

            system = platform.system()
            if system == 'Windows':
                import os
                os.startfile(file_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=True)
            return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False

    @staticmethod
    def open_folder(file_path: str) -> bool:
        """
        Open folder containing the file

        Args:
            file_path: Path to file

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            folder = path.parent
            if not folder.exists():
                return False

            system = platform.system()
            if system == 'Windows':
                subprocess.run(['explorer', '/select,', str(path)], check=True)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', '-R', str(path)], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(folder)], check=True)
            return True
        except Exception as e:
            print(f"Error opening folder: {e}")
            return False

    @staticmethod
    def ensure_pdf_extension(file_path: str) -> str:
        """
        Ensure file path has .pdf extension

        Args:
            file_path: File path

        Returns:
            File path with .pdf extension
        """
        if not file_path.lower().endswith('.pdf'):
            return file_path + '.pdf'
        return file_path

    @staticmethod
    def get_unique_filename(file_path: str) -> str:
        """
        Get unique filename if file already exists

        Args:
            file_path: Desired file path

        Returns:
            Unique file path
        """
        path = Path(file_path)
        if not path.exists():
            return file_path

        # Add counter to filename
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1

        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return str(new_path)
            counter += 1

    @staticmethod
    def validate_path(file_path: str) -> Tuple[bool, str]:
        """
        Validate file path for writing

        Args:
            file_path: File path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(file_path)

            # Check parent directory exists
            if not path.parent.exists():
                return False, "Parent directory does not exist"

            # Check parent directory is writable
            if not path.parent.is_dir():
                return False, "Parent path is not a directory"

            # Try to check write permissions
            test_file = path.parent / '.write_test'
            try:
                test_file.touch()
                test_file.unlink()
            except Exception:
                return False, "No write permission in target directory"

            return True, ""
        except Exception as e:
            return False, str(e)


class ToastNotification:
    """Toast-style notification (temporary message)"""

    @staticmethod
    def show(parent: QWidget, message: str, duration: int = 3000):
        """
        Show toast notification

        Args:
            parent: Parent widget
            message: Message to display
            duration: Duration in milliseconds
        """
        # Note: This is a simplified version
        # In a production app, you might want a custom toast widget
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.NoButton)
        msg.setWindowTitle("Notification")

        # Auto-close after duration
        QTimer.singleShot(duration, msg.close)
        msg.exec()


def generate_export_filename(export_type: str, identifier: str = "", timestamp: bool = True) -> str:
    """
    Generate standardized export filename

    Args:
        export_type: "purchase" or "delivery"
        identifier: Bill number or invoice number
        timestamp: Whether to include timestamp

    Returns:
        Generated filename
    """
    from datetime import datetime

    parts = []

    if export_type == "purchase":
        parts.append("purchase_bill")
    elif export_type == "delivery":
        parts.append("delivery_invoice")
    else:
        parts.append("export")

    if identifier:
        # Clean identifier (remove special characters)
        clean_id = "".join(c for c in identifier if c.isalnum() or c in ('-', '_'))
        parts.append(clean_id)

    if timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        parts.append(ts)

    return "_".join(parts) + ".pdf"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
