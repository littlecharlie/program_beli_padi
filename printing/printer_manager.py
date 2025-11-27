"""
Printer Manager
Manages printing to Epson LQ-310 dot matrix printer via USB
"""
import platform
from typing import Optional, List


class PrinterManager:
    """Manage printing operations for Epson LQ-310"""

    DEFAULT_PRINTER_NAME = "EPSON LQ-310"
    TIMEOUT = 30000  # milliseconds

    @staticmethod
    def get_system_platform() -> str:
        """Get current operating system"""
        return platform.system()

    @staticmethod
    def get_available_printers() -> List[str]:
        """
        Get list of available printers on the system

        Returns:
            List of printer names
        """
        system = PrinterManager.get_system_platform()

        if system == "Windows":
            return PrinterManager._get_windows_printers()
        elif system == "Linux":
            return PrinterManager._get_linux_printers()
        elif system == "Darwin":  # macOS
            return PrinterManager._get_macos_printers()
        else:
            return []

    @staticmethod
    def _get_windows_printers() -> List[str]:
        """Get printers on Windows system"""
        try:
            import win32print
            return [printer[2] for printer in win32print.EnumPrinters(2)]
        except ImportError:
            print("win32print not installed. Install with: pip install pywin32")
            return []

    @staticmethod
    def _get_linux_printers() -> List[str]:
        """Get printers on Linux system"""
        try:
            import cups
            conn = cups.Connection()
            printers = conn.getPrinters()
            return list(printers.keys())
        except ImportError:
            print("python-cups not installed. Install with: pip install pycups")
            return []

    @staticmethod
    def _get_macos_printers() -> List[str]:
        """Get printers on macOS system"""
        try:
            import cups
            conn = cups.Connection()
            printers = conn.getPrinters()
            return list(printers.keys())
        except ImportError:
            print("python-cups not installed. Install with: pip install pycups")
            return []

    @staticmethod
    def find_printer(name_pattern: str = "LQ-310") -> Optional[str]:
        """
        Find printer by name pattern

        Args:
            name_pattern: Pattern to search for (case-insensitive)

        Returns:
            Printer name if found, None otherwise
        """
        printers = PrinterManager.get_available_printers()
        pattern_upper = name_pattern.upper()

        for printer in printers:
            if pattern_upper in printer.upper():
                return printer

        return None

    @staticmethod
    def print_receipt_windows(receipt_text: str, printer_name: Optional[str] = None) -> bool:
        """
        Print receipt on Windows using win32print

        Args:
            receipt_text: Formatted receipt text with ESC/P commands
            printer_name: Optional printer name (auto-detect if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            import win32print

            if not printer_name:
                printer_name = PrinterManager.find_printer()
                if not printer_name:
                    print("Epson LQ-310 printer not found")
                    return False

            print(f"Printing to: {printer_name}")

            # Open printer
            hprinter = win32print.OpenPrinter(printer_name)

            try:
                # Start print job
                job_info = ("Rice Purchase Receipt", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)

                try:
                    # Start page
                    win32print.StartPagePrinter(hprinter)

                    # Send data to printer (encode to bytes)
                    # Use cp437 for extended ASCII characters
                    win32print.WritePrinter(hprinter, receipt_text.encode('cp437', errors='ignore'))

                    # End page
                    win32print.EndPagePrinter(hprinter)

                finally:
                    # End document
                    win32print.EndDocPrinter(hprinter)

            finally:
                # Close printer
                win32print.ClosePrinter(hprinter)

            print("Receipt printed successfully")
            return True

        except ImportError:
            print("pywin32 not installed. Install with: pip install pywin32")
            return False
        except Exception as e:
            print(f"Print error: {str(e)}")
            return False

    @staticmethod
    def print_receipt_linux(receipt_text: str, printer_name: Optional[str] = None) -> bool:
        """
        Print receipt on Linux using CUPS

        Args:
            receipt_text: Formatted receipt text with ESC/P commands
            printer_name: Optional printer name (auto-detect if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            import cups

            if not printer_name:
                printer_name = PrinterManager.find_printer()
                if not printer_name:
                    print("Epson LQ-310 printer not found")
                    return False

            print(f"Printing to: {printer_name}")

            # Connect to CUPS
            conn = cups.Connection()

            # Print raw data
            job_id = conn.printFile(
                printer_name,
                receipt_text,
                "Receipt",
                {}
            )

            print(f"Receipt queued for printing (Job ID: {job_id})")
            return True

        except ImportError:
            print("pycups not installed. Install with: pip install pycups")
            return False
        except Exception as e:
            print(f"Print error: {str(e)}")
            return False

    @staticmethod
    def print_receipt(receipt_text: str, printer_name: Optional[str] = None) -> bool:
        """
        Print receipt to Epson LQ-310 (platform-independent)

        Args:
            receipt_text: Formatted receipt text with ESC/P commands
            printer_name: Optional printer name (auto-detect if None)

        Returns:
            True if successful, False otherwise
        """
        system = PrinterManager.get_system_platform()

        if system == "Windows":
            return PrinterManager.print_receipt_windows(receipt_text, printer_name)
        elif system in ("Linux", "Darwin"):
            return PrinterManager.print_receipt_linux(receipt_text, printer_name)
        else:
            print(f"Unsupported platform: {system}")
            return False

    @staticmethod
    def print_to_file(receipt_text: str, filename: str = "receipt_output.txt") -> bool:
        """
        Write receipt to file (for testing/debugging)

        Args:
            receipt_text: Formatted receipt text
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(receipt_text)

            print(f"Receipt saved to: {filename}")
            return True

        except Exception as e:
            print(f"Error writing to file: {str(e)}")
            return False

    @staticmethod
    def test_printer_connection(printer_name: Optional[str] = None) -> bool:
        """
        Test connection to printer

        Args:
            printer_name: Optional printer name (auto-detect if None)

        Returns:
            True if printer is available, False otherwise
        """
        if not printer_name:
            printer_name = PrinterManager.find_printer()

        if not printer_name:
            print("No Epson LQ-310 printer found")
            return False

        print(f"Printer found: {printer_name}")
        return True
