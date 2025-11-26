"""
Receipt PDF Service
Converts text-based receipt output to PDF format with monospace font
Maintains the dot matrix printer appearance for digital archiving
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from sqlalchemy.orm import Session

from models.purchase_bill import PurchaseBill
from models.delivery_invoice import DeliveryInvoice
from printing.purchase_receipt import PurchaseReceiptFormatter
from printing.delivery_receipt import DeliveryReceiptFormatter
from services.config_service import ConfigService


class ReceiptPdfError(Exception):
    """Base exception for receipt PDF errors"""
    pass


class ReceiptPdfService:
    """Service for converting text receipts to PDF format"""

    # PDF Configuration
    PAGE_WIDTH, PAGE_HEIGHT = A4
    MARGIN_LEFT = 20 * mm
    MARGIN_TOP = 20 * mm
    MARGIN_BOTTOM = 20 * mm

    # Font settings for monospace appearance (like dot matrix)
    FONT_NAME = 'Courier'  # Built-in monospace font
    FONT_SIZE = 9  # Smaller font to fit 80 columns
    LINE_HEIGHT = 12  # Points between lines

    # Characters per line (80 for receipt templates)
    CHARS_PER_LINE = 80

    @staticmethod
    def _get_export_directory() -> Path:
        """Get or create receipt PDF export directory"""
        export_dir = os.getenv('RECEIPT_PDF_DIR', './exports/receipts')
        path = Path(export_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _get_company_info(db: Session) -> dict:
        """Get company information from config"""
        return {
            'name': ConfigService.get_value(db, 'company_name', 'AYOP BIN ARSHAD'),
            'address_1': ConfigService.get_value(
                db, 'company_address',
                'LOT 49, PARIT 10, PASIR PANJANG, 45400 SEKINCHAN, SELANGOR'
            ),
            'address_2': ConfigService.get_value(
                db, 'company_address_2', 'SELANGOR DARUL EHSAN'
            ),
            'registration': ConfigService.get_value(db, 'company_registration', '474523-K'),
            'phone': ConfigService.get_value(db, 'company_phone', '0162120051')
        }

    @staticmethod
    def _create_pdf_from_text(
        receipt_text: str,
        output_path: Optional[str] = None,
        return_bytes: bool = False,
        title: str = "Receipt"
    ) -> Union[str, bytes]:
        """
        Create PDF from text receipt with monospace font

        Args:
            receipt_text: Text content of receipt
            output_path: Optional file path for PDF
            return_bytes: If True, return bytes instead of saving
            title: PDF document title

        Returns:
            File path (str) or PDF bytes (bytes)
        """
        try:
            # Create canvas
            if return_bytes:
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
            else:
                if not output_path:
                    raise ReceiptPdfError("Output path required when not returning bytes")
                c = canvas.Canvas(output_path, pagesize=A4)

            # Set PDF metadata
            c.setTitle(title)
            c.setAuthor("Rice Billing System")
            c.setSubject("Receipt")

            # Set font to monospace
            c.setFont(ReceiptPdfService.FONT_NAME, ReceiptPdfService.FONT_SIZE)

            # Split text into lines
            lines = receipt_text.split('\n')

            # Calculate starting Y position (from top)
            y_position = ReceiptPdfService.PAGE_HEIGHT - ReceiptPdfService.MARGIN_TOP

            # Draw each line
            for line in lines:
                # Check if we need a new page
                if y_position < ReceiptPdfService.MARGIN_BOTTOM:
                    c.showPage()
                    c.setFont(ReceiptPdfService.FONT_NAME, ReceiptPdfService.FONT_SIZE)
                    y_position = ReceiptPdfService.PAGE_HEIGHT - ReceiptPdfService.MARGIN_TOP

                # Draw the line
                c.drawString(ReceiptPdfService.MARGIN_LEFT, y_position, line)

                # Move to next line
                y_position -= ReceiptPdfService.LINE_HEIGHT

            # Save the PDF
            c.save()

            if return_bytes:
                pdf_bytes = buffer.getvalue()
                buffer.close()
                return pdf_bytes
            else:
                return output_path

        except Exception as e:
            raise ReceiptPdfError(f"Failed to create PDF from receipt text: {str(e)}")

    @staticmethod
    def export_purchase_receipt_pdf(
        db: Session,
        bill_id: int,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Export purchase bill receipt to PDF

        Args:
            db: Database session
            bill_id: Purchase bill ID
            output_path: Optional custom output path (if None, auto-generated)
            return_bytes: If True, return bytes instead of saving to file

        Returns:
            File path (str) or PDF bytes (bytes) depending on return_bytes

        Raises:
            ReceiptPdfError: If PDF generation fails
        """
        try:
            # Fetch purchase bill
            bill = db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()

            if not bill:
                raise ReceiptPdfError(f"Purchase bill with ID {bill_id} not found")

            # Get company info
            company_info = ReceiptPdfService._get_company_info(db)

            # Generate receipt text
            receipt_text = PurchaseReceiptFormatter.format_receipt(bill, company_info)

            # Determine output path
            if not return_bytes and not output_path:
                export_dir = ReceiptPdfService._get_export_directory()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"receipt_purchase_{bill.bill_number}_{timestamp}.pdf"
                output_path = str(export_dir / filename)

            # Create PDF
            result = ReceiptPdfService._create_pdf_from_text(
                receipt_text=receipt_text,
                output_path=output_path,
                return_bytes=return_bytes,
                title=f"Purchase Bill Receipt - {bill.bill_number}"
            )

            return result

        except Exception as e:
            raise ReceiptPdfError(f"Failed to export purchase receipt to PDF: {str(e)}")

    @staticmethod
    def export_delivery_receipt_pdf(
        db: Session,
        invoice_id: int,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Export delivery invoice receipt to PDF

        Args:
            db: Database session
            invoice_id: Delivery invoice ID
            output_path: Optional custom output path (if None, auto-generated)
            return_bytes: If True, return bytes instead of saving to file

        Returns:
            File path (str) or PDF bytes (bytes) depending on return_bytes

        Raises:
            ReceiptPdfError: If PDF generation fails
        """
        try:
            # Fetch delivery invoice
            invoice = db.query(DeliveryInvoice).filter(
                DeliveryInvoice.id == invoice_id
            ).first()

            if not invoice:
                raise ReceiptPdfError(f"Delivery invoice with ID {invoice_id} not found")

            # Get company info
            company_info = ReceiptPdfService._get_company_info(db)

            # Generate receipt text
            receipt_text = DeliveryReceiptFormatter.format_receipt(invoice, company_info)

            # Determine output path
            if not return_bytes and not output_path:
                export_dir = ReceiptPdfService._get_export_directory()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"receipt_delivery_{invoice.invoice_number}_{timestamp}.pdf"
                output_path = str(export_dir / filename)

            # Create PDF
            result = ReceiptPdfService._create_pdf_from_text(
                receipt_text=receipt_text,
                output_path=output_path,
                return_bytes=return_bytes,
                title=f"Delivery Invoice Receipt - {invoice.invoice_number}"
            )

            return result

        except Exception as e:
            raise ReceiptPdfError(f"Failed to export delivery receipt to PDF: {str(e)}")

    @staticmethod
    def print_and_export(
        db: Session,
        bill_or_invoice_id: int,
        receipt_type: str,
        do_print: bool = True,
        do_export: bool = True,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Print to physical printer and/or export to PDF

        Args:
            db: Database session
            bill_or_invoice_id: Purchase bill or delivery invoice ID
            receipt_type: 'purchase' or 'delivery'
            do_print: If True, print to physical printer
            do_export: If True, export to PDF
            output_path: Optional custom PDF output path

        Returns:
            PDF file path if exported, None otherwise

        Raises:
            ReceiptPdfError: If operation fails
        """
        try:
            pdf_path = None

            # Get company info
            company_info = ReceiptPdfService._get_company_info(db)

            if receipt_type == 'purchase':
                # Get purchase bill
                bill = db.query(PurchaseBill).filter(
                    PurchaseBill.id == bill_or_invoice_id
                ).first()

                if not bill:
                    raise ReceiptPdfError(f"Purchase bill with ID {bill_or_invoice_id} not found")

                # Generate receipt text
                receipt_text = PurchaseReceiptFormatter.format_receipt(bill, company_info)

                # Print to console/printer
                if do_print:
                    print(receipt_text)
                    # TODO: Add actual printer integration here
                    # from printing.printer_manager import PrinterManager
                    # PrinterManager.print_receipt(receipt_text)

                # Export to PDF
                if do_export:
                    pdf_path = ReceiptPdfService.export_purchase_receipt_pdf(
                        db=db,
                        bill_id=bill_or_invoice_id,
                        output_path=output_path,
                        return_bytes=False
                    )

            elif receipt_type == 'delivery':
                # Get delivery invoice
                invoice = db.query(DeliveryInvoice).filter(
                    DeliveryInvoice.id == bill_or_invoice_id
                ).first()

                if not invoice:
                    raise ReceiptPdfError(f"Delivery invoice with ID {bill_or_invoice_id} not found")

                # Generate receipt text
                receipt_text = DeliveryReceiptFormatter.format_receipt(invoice, company_info)

                # Print to console/printer
                if do_print:
                    print(receipt_text)
                    # TODO: Add actual printer integration here
                    # from printing.printer_manager import PrinterManager
                    # PrinterManager.print_receipt(receipt_text)

                # Export to PDF
                if do_export:
                    pdf_path = ReceiptPdfService.export_delivery_receipt_pdf(
                        db=db,
                        invoice_id=bill_or_invoice_id,
                        output_path=output_path,
                        return_bytes=False
                    )
            else:
                raise ReceiptPdfError(f"Invalid receipt type: {receipt_type}")

            return pdf_path

        except Exception as e:
            raise ReceiptPdfError(f"Failed to print/export receipt: {str(e)}")
