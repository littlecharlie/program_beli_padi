"""
PDF Export Service
Generates professional PDF documents for purchase bills, delivery invoices, and reports
"""
import os
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Union, BinaryIO
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO

from models.purchase_bill import PurchaseBill
from models.delivery_invoice import DeliveryInvoice
from models.farmer import Farmer
from models.rice_mill import RiceMill
from models.truck import Truck
from models.harvest_area import HarvestArea
from services.config_service import ConfigService
from services.calculation_service import CalculationService


class PdfExportError(Exception):
    """Base exception for PDF export errors"""
    pass


class PurchaseBillNotFoundError(PdfExportError):
    """Raised when purchase bill is not found"""
    pass


class DeliveryInvoiceNotFoundError(PdfExportError):
    """Raised when delivery invoice is not found"""
    pass


class InvalidDateRangeError(PdfExportError):
    """Raised when date range is invalid"""
    pass


class PdfExportService:
    """Service for generating PDF documents"""

    # PDF Configuration
    PAGE_WIDTH, PAGE_HEIGHT = A4
    MARGIN = 15 * mm

    @staticmethod
    def _get_export_directory() -> Path:
        """Get or create PDF export directory"""
        # Check environment variable first
        export_dir = os.getenv('PDF_EXPORT_DIR', './exports/pdf')
        path = Path(export_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _format_currency(amount: Union[float, Decimal]) -> str:
        """Format currency value with RM prefix"""
        if isinstance(amount, Decimal):
            amount = float(amount)
        return f"RM {amount:,.2f}"

    @staticmethod
    def _format_weight(weight: Union[float, Decimal]) -> str:
        """Format weight value with kg suffix"""
        if isinstance(weight, Decimal):
            weight = float(weight)
        return f"{weight:,.2f} kg"

    @staticmethod
    def _format_date(dt: datetime) -> str:
        """Format datetime to Malaysian date format"""
        if isinstance(dt, datetime):
            return dt.strftime('%d/%m/%Y')
        elif isinstance(dt, date):
            return dt.strftime('%d/%m/%Y')
        return str(dt)

    @staticmethod
    def _get_company_info(db: Session) -> dict:
        """Get company information from config"""
        return {
            'name': os.getenv('COMPANY_NAME', ConfigService.get_value(db, 'company_name', 'AYOP BIN ARSHAD')),
            'address_1': os.getenv('COMPANY_ADDRESS_1', ConfigService.get_value(db, 'company_address_1', '')),
            'address_2': os.getenv('COMPANY_ADDRESS_2', ConfigService.get_value(db, 'company_address_2', '')),
            'registration': os.getenv('COMPANY_REGISTRATION', ConfigService.get_value(db, 'company_registration', '')),
            'phone': os.getenv('COMPANY_PHONE', ConfigService.get_value(db, 'company_phone', '')),
        }

    @staticmethod
    def _create_styles():
        """Create custom paragraph styles for PDF"""
        styles = getSampleStyleSheet()

        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Company info style
        styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#555555'),
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Field label style
        styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica-Bold'
        ))

        # Field value style
        styles.add(ParagraphStyle(
            name='FieldValue',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1a1a1a'),
            fontName='Helvetica'
        ))

        return styles

    @staticmethod
    def _create_header(company_info: dict, styles) -> List:
        """Create PDF header with company information"""
        elements = []

        # Company name
        elements.append(Paragraph(company_info['name'], styles['CustomTitle']))

        # Address lines
        if company_info['address_1']:
            elements.append(Paragraph(company_info['address_1'], styles['CompanyInfo']))
        if company_info['address_2']:
            elements.append(Paragraph(company_info['address_2'], styles['CompanyInfo']))

        # Registration and phone
        info_line = ""
        if company_info['registration']:
            info_line += f"No Lesen: {company_info['registration']}"
        if company_info['phone']:
            if info_line:
                info_line += " | "
            info_line += f"Tel: {company_info['phone']}"

        if info_line:
            elements.append(Paragraph(info_line, styles['CompanyInfo']))

        elements.append(Spacer(1, 10))

        return elements

    @staticmethod
    def export_purchase_bill(
        db: Session,
        bill_id: int,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Export single purchase bill to PDF

        Args:
            db: Database session
            bill_id: Purchase bill ID
            output_path: Optional custom output path (if None, auto-generated)
            return_bytes: If True, return bytes instead of saving to file

        Returns:
            File path (str) or PDF bytes (bytes) depending on return_bytes

        Raises:
            PurchaseBillNotFoundError: If bill not found
            PdfExportError: If PDF generation fails
        """
        try:
            # Fetch purchase bill with all relationships
            bill = db.query(PurchaseBill).options(
                joinedload(PurchaseBill.farmer),
                joinedload(PurchaseBill.truck),
                joinedload(PurchaseBill.harvest_area)
            ).filter(PurchaseBill.id == bill_id).first()

            if not bill:
                raise PurchaseBillNotFoundError(f"Purchase bill with ID {bill_id} not found")

            # Get farmer info
            farmer = db.query(Farmer).filter(Farmer.id == bill.farmer_id).first()
            truck = db.query(Truck).filter(Truck.id == bill.truck_id).first() if bill.truck_id else None
            harvest_area = db.query(HarvestArea).filter(HarvestArea.id == bill.harvest_area_id).first() if bill.harvest_area_id else None

            # Determine output destination
            if return_bytes:
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )
            else:
                if not output_path:
                    export_dir = PdfExportService._get_export_directory()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"purchase_bill_{bill.bill_number}_{timestamp}.pdf"
                    output_path = str(export_dir / filename)

                doc = SimpleDocTemplate(
                    output_path,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )

            # Build PDF content
            elements = []
            styles = PdfExportService._create_styles()
            company_info = PdfExportService._get_company_info(db)

            # Add header
            elements.extend(PdfExportService._create_header(company_info, styles))

            # Document title
            elements.append(Paragraph("BIL BELIAN PADI", styles['CustomTitle']))
            elements.append(Spacer(1, 5))

            # Bill number and date
            bill_info_data = [
                ["Bil Belian:", bill.bill_number, "Tarikh:", PdfExportService._format_date(bill.bill_date)]
            ]
            bill_info_table = Table(bill_info_data, colWidths=[60, 120, 50, 100])
            bill_info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            elements.append(bill_info_table)
            elements.append(Spacer(1, 10))

            # Farmer information section
            farmer_data = [
                ["MAKLUMAT PETANI", ""],
                ["Nama:", farmer.name if farmer else "N/A"],
                ["No. K/P:", farmer.ic_number if farmer else "N/A"],
                ["Alamat:", farmer.address if farmer and farmer.address else "N/A"],
                ["No. Telefon:", farmer.phone if farmer and farmer.phone else "N/A"],
                ["No. Daftar Pesawah:", farmer.registration_number if farmer and farmer.registration_number else "N/A"],
                ["No. Kad Subsidi:", farmer.subsidy_code if farmer and farmer.subsidy_code else "N/A"],
                ["No. Akaun Bank:", farmer.bank_account if farmer and farmer.bank_account else "N/A"],
            ]

            farmer_table = Table(farmer_data, colWidths=[120, 300])
            farmer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(farmer_table)
            elements.append(Spacer(1, 10))

            # Weighing information
            weighing_data = [
                ["MAKLUMAT TIMBANGAN", ""],
                ["No. Lori:", truck.truck_number if truck else "N/A"],
                ["No. Resit Timbang:", bill.weighbridge_receipt if bill.weighbridge_receipt else "N/A"],
                ["Kawasan Tuaian:", harvest_area.area_name if harvest_area else "N/A"],
            ]

            weighing_table = Table(weighing_data, colWidths=[120, 300])
            weighing_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(weighing_table)
            elements.append(Spacer(1, 10))

            # Discount breakdown
            discount_data = [
                ["POTONGAN", ""],
                ["Wap Basah:", f"{float(bill.discount_wap_basah):.2f}%"],
                ["Hampa Padi:", f"{float(bill.discount_hampa_padi):.2f}%"],
                ["Padi Muda/Rosak:", f"{float(bill.discount_padi_muda):.2f}%"],
                ["Jumlah Potongan:", f"{float(bill.total_discount_percent):.2f}%"],
            ]

            discount_table = Table(discount_data, colWidths=[120, 300])
            discount_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#e8f4f8')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(discount_table)
            elements.append(Spacer(1, 10))

            # Weight and payment calculations
            calculation_data = [
                ["KIRAAN", ""],
                ["Berat Timbangan (Gross):", PdfExportService._format_weight(bill.gross_weight)],
                ["Potongan Berat:", PdfExportService._format_weight(bill.discount_weight)],
                ["Berat Bersih (Net):", PdfExportService._format_weight(bill.net_weight)],
                ["Harga (per 1000kg):", PdfExportService._format_currency(bill.rice_price_per_1000kg)],
                ["", ""],
                ["Nilai Padi:", PdfExportService._format_currency(bill.total_payment)],
                ["Anggaran Subsidi:", PdfExportService._format_currency(bill.subsidy_estimate)],
                ["", ""],
                ["JUMLAH BAYARAN:", PdfExportService._format_currency(bill.total_payment)],
            ]

            calculation_table = Table(calculation_data, colWidths=[120, 300])
            calculation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('BACKGROUND', (0, 9), (-1, 9), colors.HexColor('#d4edda')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 9), (-1, 9), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTSIZE', (0, 9), (-1, 9), 11),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEABOVE', (0, 9), (-1, 9), 2, colors.HexColor('#28a745')),
            ]))
            elements.append(calculation_table)

            # Build PDF
            doc.build(elements)

            if return_bytes:
                pdf_bytes = buffer.getvalue()
                buffer.close()
                return pdf_bytes
            else:
                return output_path

        except PurchaseBillNotFoundError:
            raise
        except Exception as e:
            raise PdfExportError(f"Failed to generate PDF for purchase bill: {str(e)}")

    @staticmethod
    def export_delivery_invoice(
        db: Session,
        invoice_id: int,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Export single delivery invoice to PDF

        Args:
            db: Database session
            invoice_id: Delivery invoice ID
            output_path: Optional custom output path
            return_bytes: If True, return bytes instead of saving to file

        Returns:
            File path (str) or PDF bytes (bytes)

        Raises:
            DeliveryInvoiceNotFoundError: If invoice not found
            PdfExportError: If PDF generation fails
        """
        try:
            # Fetch delivery invoice with relationships
            invoice = db.query(DeliveryInvoice).options(
                joinedload(DeliveryInvoice.mill),
                joinedload(DeliveryInvoice.truck)
            ).filter(DeliveryInvoice.id == invoice_id).first()

            if not invoice:
                raise DeliveryInvoiceNotFoundError(f"Delivery invoice with ID {invoice_id} not found")

            # Get related data
            mill = db.query(RiceMill).filter(RiceMill.id == invoice.mill_id).first()
            truck = db.query(Truck).filter(Truck.id == invoice.truck_id).first()

            # Get all purchase bills in this delivery
            purchase_bills = db.query(PurchaseBill).filter(
                PurchaseBill.delivery_invoice_id == invoice_id
            ).options(joinedload(PurchaseBill.farmer)).all()

            # Determine output destination
            if return_bytes:
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )
            else:
                if not output_path:
                    export_dir = PdfExportService._get_export_directory()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"delivery_invoice_{invoice.invoice_number}_{timestamp}.pdf"
                    output_path = str(export_dir / filename)

                doc = SimpleDocTemplate(
                    output_path,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )

            # Build PDF content
            elements = []
            styles = PdfExportService._create_styles()
            company_info = PdfExportService._get_company_info(db)

            # Add header
            elements.extend(PdfExportService._create_header(company_info, styles))

            # Document title
            elements.append(Paragraph("INVOIS HANTARAN", styles['CustomTitle']))
            elements.append(Spacer(1, 5))

            # Invoice info
            invoice_info_data = [
                ["No. Invois:", invoice.invoice_number, "Tarikh:", PdfExportService._format_date(invoice.invoice_date)]
            ]
            invoice_info_table = Table(invoice_info_data, colWidths=[60, 120, 50, 100])
            invoice_info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            elements.append(invoice_info_table)
            elements.append(Spacer(1, 10))

            # Delivery information
            delivery_data = [
                ["MAKLUMAT HANTARAN", ""],
                ["Kepada:", mill.mill_name if mill else "N/A"],
                ["Alamat Kilang:", mill.address if mill and mill.address else "N/A"],
                ["No. Telefon Kilang:", mill.phone if mill and mill.phone else "N/A"],
                ["No. Lori:", truck.truck_number if truck else "N/A"],
                ["Berat Lori:", PdfExportService._format_weight(truck.tare_weight) if truck and truck.tare_weight else "N/A"],
            ]

            delivery_table = Table(delivery_data, colWidths=[120, 300])
            delivery_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(delivery_table)
            elements.append(Spacer(1, 15))

            # Purchase bills table
            elements.append(Paragraph("SENARAI BIL BELIAN", styles['CustomSubtitle']))
            elements.append(Spacer(1, 5))

            # Table header
            bills_data = [["Bil", "No. Bil Belian", "Nama Petani", "Berat Bersih (kg)", "Tarikh"]]

            # Add purchase bills
            for idx, bill in enumerate(purchase_bills, 1):
                farmer = db.query(Farmer).filter(Farmer.id == bill.farmer_id).first()
                bills_data.append([
                    str(idx),
                    bill.bill_number,
                    farmer.name if farmer else "N/A",
                    f"{float(bill.net_weight):,.2f}",
                    PdfExportService._format_date(bill.bill_date)
                ])

            # Add total row
            bills_data.append([
                "", "", "JUMLAH:",
                f"{float(invoice.total_weight):,.2f}",
                ""
            ])

            bills_table = Table(bills_data, colWidths=[30, 70, 150, 80, 60])
            bills_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4edda')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#28a745')),
            ]))
            elements.append(bills_table)

            # Build PDF
            doc.build(elements)

            if return_bytes:
                pdf_bytes = buffer.getvalue()
                buffer.close()
                return pdf_bytes
            else:
                return output_path

        except DeliveryInvoiceNotFoundError:
            raise
        except Exception as e:
            raise PdfExportError(f"Failed to generate PDF for delivery invoice: {str(e)}")

    @staticmethod
    def export_multiple_bills_batch(
        db: Session,
        bill_ids: List[int],
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Export multiple purchase bills in a single PDF document

        Args:
            db: Database session
            bill_ids: List of purchase bill IDs
            output_path: Optional custom output path
            return_bytes: If True, return bytes instead of saving to file

        Returns:
            File path (str) or PDF bytes (bytes)

        Raises:
            PdfExportError: If PDF generation fails
        """
        try:
            if not bill_ids:
                raise PdfExportError("No bill IDs provided for batch export")

            # Determine output destination
            if return_bytes:
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )
            else:
                if not output_path:
                    export_dir = PdfExportService._get_export_directory()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"purchase_bills_batch_{timestamp}.pdf"
                    output_path = str(export_dir / filename)

                doc = SimpleDocTemplate(
                    output_path,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )

            elements = []
            styles = PdfExportService._create_styles()
            company_info = PdfExportService._get_company_info(db)

            # Process each bill
            for idx, bill_id in enumerate(bill_ids):
                # Fetch bill
                bill = db.query(PurchaseBill).options(
                    joinedload(PurchaseBill.farmer),
                    joinedload(PurchaseBill.truck),
                    joinedload(PurchaseBill.harvest_area)
                ).filter(PurchaseBill.id == bill_id).first()

                if not bill:
                    continue  # Skip missing bills

                # Add header only for first bill
                if idx == 0:
                    elements.extend(PdfExportService._create_header(company_info, styles))
                    elements.append(Paragraph("BIL BELIAN PADI - BATCH EXPORT", styles['CustomTitle']))
                    elements.append(Spacer(1, 10))

                # Add page break between bills (except first)
                if idx > 0:
                    elements.append(PageBreak())

                # Add bill content (simplified version)
                elements.append(Paragraph(f"BIL BELIAN: {bill.bill_number}", styles['CustomSubtitle']))
                elements.append(Spacer(1, 5))

                # Get related data
                farmer = db.query(Farmer).filter(Farmer.id == bill.farmer_id).first()
                truck = db.query(Truck).filter(Truck.id == bill.truck_id).first() if bill.truck_id else None

                # Summary table
                summary_data = [
                    ["Tarikh:", PdfExportService._format_date(bill.bill_date)],
                    ["Nama Petani:", farmer.name if farmer else "N/A"],
                    ["No. K/P:", farmer.ic_number if farmer else "N/A"],
                    ["No. Lori:", truck.truck_number if truck else "N/A"],
                    ["Berat Timbangan:", PdfExportService._format_weight(bill.gross_weight)],
                    ["Potongan:", f"{float(bill.total_discount_percent):.2f}%"],
                    ["Berat Bersih:", PdfExportService._format_weight(bill.net_weight)],
                    ["Jumlah Bayaran:", PdfExportService._format_currency(bill.total_payment)],
                ]

                summary_table = Table(summary_data, colWidths=[120, 300])
                summary_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ]))
                elements.append(summary_table)

            # Build PDF
            doc.build(elements)

            if return_bytes:
                pdf_bytes = buffer.getvalue()
                buffer.close()
                return pdf_bytes
            else:
                return output_path

        except Exception as e:
            raise PdfExportError(f"Failed to generate batch PDF: {str(e)}")

    @staticmethod
    def export_date_range_report(
        db: Session,
        start_date: date,
        end_date: date,
        report_type: str = 'purchase',
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Export date range report to PDF

        Args:
            db: Database session
            start_date: Start date of range
            end_date: End date of range
            report_type: Type of report ('purchase' or 'delivery')
            output_path: Optional custom output path
            return_bytes: If True, return bytes instead of saving to file

        Returns:
            File path (str) or PDF bytes (bytes)

        Raises:
            InvalidDateRangeError: If date range is invalid
            PdfExportError: If PDF generation fails
        """
        try:
            # Validate date range
            if start_date > end_date:
                raise InvalidDateRangeError("Start date must be before or equal to end date")

            # Determine output destination
            if return_bytes:
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )
            else:
                if not output_path:
                    export_dir = PdfExportService._get_export_directory()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{report_type}_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{timestamp}.pdf"
                    output_path = str(export_dir / filename)

                doc = SimpleDocTemplate(
                    output_path,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )

            elements = []
            styles = PdfExportService._create_styles()
            company_info = PdfExportService._get_company_info(db)

            # Add header
            elements.extend(PdfExportService._create_header(company_info, styles))

            if report_type == 'purchase':
                # Purchase bills report
                elements.append(Paragraph("LAPORAN BIL BELIAN", styles['CustomTitle']))
                elements.append(Spacer(1, 3))
                elements.append(Paragraph(
                    f"Tarikh: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
                    styles['CompanyInfo']
                ))
                elements.append(Spacer(1, 10))

                # Fetch purchase bills in date range
                bills = db.query(PurchaseBill).filter(
                    PurchaseBill.bill_date >= start_date,
                    PurchaseBill.bill_date <= end_date
                ).order_by(PurchaseBill.bill_date).all()

                # Summary statistics
                total_bills = len(bills)
                total_weight = sum(float(bill.net_weight) for bill in bills)
                total_payment = sum(float(bill.total_payment) for bill in bills)

                summary_data = [
                    ["RINGKASAN", ""],
                    ["Jumlah Bil Belian:", str(total_bills)],
                    ["Jumlah Berat Bersih:", f"{total_weight:,.2f} kg"],
                    ["Jumlah Bayaran:", PdfExportService._format_currency(total_payment)],
                ]

                summary_table = Table(summary_data, colWidths=[150, 250])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 15))

                # Detailed bills table
                elements.append(Paragraph("SENARAI TERPERINCI", styles['CustomSubtitle']))
                elements.append(Spacer(1, 5))

                bills_data = [["No.", "Bil", "Tarikh", "Petani", "Berat (kg)", "Bayaran (RM)"]]

                for idx, bill in enumerate(bills, 1):
                    farmer = db.query(Farmer).filter(Farmer.id == bill.farmer_id).first()
                    bills_data.append([
                        str(idx),
                        bill.bill_number,
                        PdfExportService._format_date(bill.bill_date),
                        farmer.name[:20] if farmer else "N/A",
                        f"{float(bill.net_weight):,.2f}",
                        f"{float(bill.total_payment):,.2f}"
                    ])

                bills_table = Table(bills_data, colWidths=[25, 50, 60, 120, 70, 70])
                bills_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (4, 0), (5, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(bills_table)

            else:  # delivery report
                # Delivery invoices report
                elements.append(Paragraph("LAPORAN INVOIS HANTARAN", styles['CustomTitle']))
                elements.append(Spacer(1, 3))
                elements.append(Paragraph(
                    f"Tarikh: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
                    styles['CompanyInfo']
                ))
                elements.append(Spacer(1, 10))

                # Fetch delivery invoices in date range
                invoices = db.query(DeliveryInvoice).filter(
                    DeliveryInvoice.invoice_date >= start_date,
                    DeliveryInvoice.invoice_date <= end_date
                ).order_by(DeliveryInvoice.invoice_date).all()

                # Summary statistics
                total_invoices = len(invoices)
                total_weight = sum(float(invoice.total_weight) for invoice in invoices)

                summary_data = [
                    ["RINGKASAN", ""],
                    ["Jumlah Invois Hantaran:", str(total_invoices)],
                    ["Jumlah Berat Dihantar:", f"{total_weight:,.2f} kg"],
                ]

                summary_table = Table(summary_data, colWidths=[150, 250])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 15))

                # Detailed invoices table
                elements.append(Paragraph("SENARAI TERPERINCI", styles['CustomSubtitle']))
                elements.append(Spacer(1, 5))

                invoices_data = [["No.", "No. Invois", "Tarikh", "Kilang", "Lori", "Berat (kg)"]]

                for idx, invoice in enumerate(invoices, 1):
                    mill = db.query(RiceMill).filter(RiceMill.id == invoice.mill_id).first()
                    truck = db.query(Truck).filter(Truck.id == invoice.truck_id).first()
                    invoices_data.append([
                        str(idx),
                        invoice.invoice_number,
                        PdfExportService._format_date(invoice.invoice_date),
                        mill.mill_name[:25] if mill else "N/A",
                        truck.truck_number if truck else "N/A",
                        f"{float(invoice.total_weight):,.2f}"
                    ])

                invoices_table = Table(invoices_data, colWidths=[25, 50, 60, 130, 60, 70])
                invoices_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (5, 0), (5, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(invoices_table)

            # Build PDF
            doc.build(elements)

            if return_bytes:
                pdf_bytes = buffer.getvalue()
                buffer.close()
                return pdf_bytes
            else:
                return output_path

        except InvalidDateRangeError:
            raise
        except Exception as e:
            raise PdfExportError(f"Failed to generate date range report: {str(e)}")

    @staticmethod
    def export_farmer_summary_report(
        db: Session,
        start_date: date,
        end_date: date,
        farmer_id: Optional[int] = None,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Export farmer summary report to PDF

        Args:
            db: Database session
            start_date: Start date of range
            end_date: End date of range
            farmer_id: Optional farmer ID to filter by (None for all farmers)
            output_path: Optional custom output path
            return_bytes: If True, return bytes instead of saving to file

        Returns:
            File path (str) or PDF bytes (bytes)

        Raises:
            InvalidDateRangeError: If date range is invalid
            PdfExportError: If PDF generation fails
        """
        try:
            # Validate date range
            if start_date > end_date:
                raise InvalidDateRangeError("Start date must be before or equal to end date")

            # Determine output destination
            if return_bytes:
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )
            else:
                if not output_path:
                    export_dir = PdfExportService._get_export_directory()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"farmer_summary_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{timestamp}.pdf"
                    output_path = str(export_dir / filename)

                doc = SimpleDocTemplate(
                    output_path,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )

            elements = []
            styles = PdfExportService._create_styles()
            company_info = PdfExportService._get_company_info(db)

            # Add header
            elements.extend(PdfExportService._create_header(company_info, styles))

            # Document title
            elements.append(Paragraph("LAPORAN RINGKASAN PETANI", styles['CustomTitle']))
            elements.append(Spacer(1, 3))
            elements.append(Paragraph(
                f"Tarikh: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
                styles['CompanyInfo']
            ))
            elements.append(Spacer(1, 10))

            # Build query
            query = db.query(
                PurchaseBill.farmer_id,
                func.count(PurchaseBill.id).label('bill_count'),
                func.sum(PurchaseBill.net_weight).label('total_weight'),
                func.sum(PurchaseBill.total_payment).label('total_payment')
            ).filter(
                PurchaseBill.bill_date >= start_date,
                PurchaseBill.bill_date <= end_date
            )

            # Filter by farmer if specified
            if farmer_id:
                query = query.filter(PurchaseBill.farmer_id == farmer_id)

            # Group by farmer
            farmer_stats = query.group_by(PurchaseBill.farmer_id).all()

            # Overall summary
            total_bills = sum(stat.bill_count for stat in farmer_stats)
            total_weight = sum(float(stat.total_weight) if stat.total_weight else 0 for stat in farmer_stats)
            total_payment = sum(float(stat.total_payment) if stat.total_payment else 0 for stat in farmer_stats)

            summary_data = [
                ["RINGKASAN KESELURUHAN", ""],
                ["Jumlah Petani:", str(len(farmer_stats))],
                ["Jumlah Bil Belian:", str(total_bills)],
                ["Jumlah Berat Bersih:", f"{total_weight:,.2f} kg"],
                ["Jumlah Bayaran:", PdfExportService._format_currency(total_payment)],
            ]

            summary_table = Table(summary_data, colWidths=[150, 250])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 15))

            # Detailed farmer table
            elements.append(Paragraph("SENARAI TERPERINCI PETANI", styles['CustomSubtitle']))
            elements.append(Spacer(1, 5))

            farmer_data = [["No.", "Nama Petani", "No. K/P", "Bil", "Berat (kg)", "Bayaran (RM)"]]

            for idx, stat in enumerate(farmer_stats, 1):
                farmer = db.query(Farmer).filter(Farmer.id == stat.farmer_id).first()
                farmer_data.append([
                    str(idx),
                    farmer.name[:25] if farmer else "N/A",
                    farmer.ic_number if farmer else "N/A",
                    str(stat.bill_count),
                    f"{float(stat.total_weight):,.2f}" if stat.total_weight else "0.00",
                    f"{float(stat.total_payment):,.2f}" if stat.total_payment else "0.00"
                ])

            farmer_table = Table(farmer_data, colWidths=[25, 120, 70, 35, 70, 70])
            farmer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (5, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(farmer_table)

            # Build PDF
            doc.build(elements)

            if return_bytes:
                pdf_bytes = buffer.getvalue()
                buffer.close()
                return pdf_bytes
            else:
                return output_path

        except InvalidDateRangeError:
            raise
        except Exception as e:
            raise PdfExportError(f"Failed to generate farmer summary report: {str(e)}")

    @staticmethod
    def export_mill_summary_report(
        db: Session,
        start_date: date,
        end_date: date,
        mill_id: Optional[int] = None,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Export mill summary report to PDF

        Args:
            db: Database session
            start_date: Start date of range
            end_date: End date of range
            mill_id: Optional mill ID to filter by (None for all mills)
            output_path: Optional custom output path
            return_bytes: If True, return bytes instead of saving to file

        Returns:
            File path (str) or PDF bytes (bytes)

        Raises:
            InvalidDateRangeError: If date range is invalid
            PdfExportError: If PDF generation fails
        """
        try:
            # Validate date range
            if start_date > end_date:
                raise InvalidDateRangeError("Start date must be before or equal to end date")

            # Determine output destination
            if return_bytes:
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )
            else:
                if not output_path:
                    export_dir = PdfExportService._get_export_directory()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"mill_summary_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{timestamp}.pdf"
                    output_path = str(export_dir / filename)

                doc = SimpleDocTemplate(
                    output_path,
                    pagesize=A4,
                    leftMargin=PdfExportService.MARGIN,
                    rightMargin=PdfExportService.MARGIN,
                    topMargin=PdfExportService.MARGIN,
                    bottomMargin=PdfExportService.MARGIN
                )

            elements = []
            styles = PdfExportService._create_styles()
            company_info = PdfExportService._get_company_info(db)

            # Add header
            elements.extend(PdfExportService._create_header(company_info, styles))

            # Document title
            elements.append(Paragraph("LAPORAN RINGKASAN KILANG", styles['CustomTitle']))
            elements.append(Spacer(1, 3))
            elements.append(Paragraph(
                f"Tarikh: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
                styles['CompanyInfo']
            ))
            elements.append(Spacer(1, 10))

            # Build query
            query = db.query(
                DeliveryInvoice.mill_id,
                func.count(DeliveryInvoice.id).label('invoice_count'),
                func.sum(DeliveryInvoice.total_weight).label('total_weight')
            ).filter(
                DeliveryInvoice.invoice_date >= start_date,
                DeliveryInvoice.invoice_date <= end_date
            )

            # Filter by mill if specified
            if mill_id:
                query = query.filter(DeliveryInvoice.mill_id == mill_id)

            # Group by mill
            mill_stats = query.group_by(DeliveryInvoice.mill_id).all()

            # Overall summary
            total_invoices = sum(stat.invoice_count for stat in mill_stats)
            total_weight = sum(float(stat.total_weight) if stat.total_weight else 0 for stat in mill_stats)

            summary_data = [
                ["RINGKASAN KESELURUHAN", ""],
                ["Jumlah Kilang:", str(len(mill_stats))],
                ["Jumlah Invois Hantaran:", str(total_invoices)],
                ["Jumlah Berat Dihantar:", f"{total_weight:,.2f} kg"],
            ]

            summary_table = Table(summary_data, colWidths=[150, 250])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 15))

            # Detailed mill table
            elements.append(Paragraph("SENARAI TERPERINCI KILANG", styles['CustomSubtitle']))
            elements.append(Spacer(1, 5))

            mill_data = [["No.", "Nama Kilang", "Alamat", "Invois", "Berat (kg)"]]

            for idx, stat in enumerate(mill_stats, 1):
                mill = db.query(RiceMill).filter(RiceMill.id == stat.mill_id).first()
                mill_data.append([
                    str(idx),
                    mill.mill_name[:30] if mill else "N/A",
                    mill.address[:40] if mill and mill.address else "N/A",
                    str(stat.invoice_count),
                    f"{float(stat.total_weight):,.2f}" if stat.total_weight else "0.00"
                ])

            mill_table = Table(mill_data, colWidths=[25, 130, 130, 45, 60])
            mill_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(mill_table)

            # Build PDF
            doc.build(elements)

            if return_bytes:
                pdf_bytes = buffer.getvalue()
                buffer.close()
                return pdf_bytes
            else:
                return output_path

        except InvalidDateRangeError:
            raise
        except Exception as e:
            raise PdfExportError(f"Failed to generate mill summary report: {str(e)}")
