"""
Delivery Receipt Formatter
Formats delivery invoices for printing on Epson LQ-310
"""
import os
from datetime import datetime
from printing.escpos_commands import EscposCommands


class DeliveryReceiptFormatter:
    """Format delivery invoices for printing"""

    LINE_WIDTH = 80

    @staticmethod
    def load_template() -> str:
        """Load delivery template from file"""
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'delivery_template.txt'
        )

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    @staticmethod
    def format_receipt(delivery_invoice, company_info: dict) -> str:
        """
        Format delivery invoice receipt

        Args:
            delivery_invoice: DeliveryInvoice model object
            company_info: Dictionary with company information

        Returns:
            Formatted receipt string
        """
        # Get bill items
        from services.delivery_service import DeliveryService
        bills = DeliveryService.get_bills_for_invoice(None, delivery_invoice.id)

        # Format bill items for template
        bill_items = []
        for bill in bills:
            farmer_name = bill.farmer.name if bill.farmer else "Unknown"
            bill_line = (
                f"{bill.bill_number:<7} "
                f"{farmer_name:<35} "
                f"{float(bill.net_weight):>10,.0f}"
            )
            bill_items.append(bill_line)

        bill_items_str = '\n'.join(bill_items)

        # Format invoice date
        invoice_date = delivery_invoice.invoice_date.strftime("%d/%m/%Y")

        # Get truck and mill info
        truck_number = delivery_invoice.truck.truck_number if delivery_invoice.truck else ""
        tare_weight = float(delivery_invoice.truck.tare_weight) if delivery_invoice.truck and delivery_invoice.truck.tare_weight else 0
        mill_name = delivery_invoice.mill.mill_name if delivery_invoice.mill else ""

        template = DeliveryReceiptFormatter.load_template()

        if not template:
            return DeliveryReceiptFormatter.generate_receipt(
                delivery_invoice, company_info, bills
            )

        # Replace placeholders
        receipt = template.format(
            invoice_number=delivery_invoice.invoice_number,
            company_name=company_info.get('name', ''),
            company_address_1=company_info.get('address_1', ''),
            company_address_2=company_info.get('address_2', ''),
            company_registration=company_info.get('registration', ''),
            company_phone=company_info.get('phone', ''),
            invoice_date=invoice_date,
            truck_number=truck_number,
            tare_weight=f"{tare_weight:,.2f}" if tare_weight else "0",
            mill_name=mill_name,
            total_weight=f"{float(delivery_invoice.total_weight):,.2f}",
            bill_items=bill_items_str
        )

        return receipt

    @staticmethod
    def generate_receipt(delivery_invoice, company_info: dict, bills: list) -> str:
        """
        Generate receipt manually if template not available

        Args:
            delivery_invoice: DeliveryInvoice model object
            company_info: Dictionary with company information
            bills: List of PurchaseBill objects

        Returns:
            Formatted receipt string
        """
        lines = []

        # Header
        lines.append(EscposCommands.separator(DeliveryReceiptFormatter.LINE_WIDTH))
        lines.append(EscposCommands.format_line(
            f"INVOIS HANTARAN                    No : {delivery_invoice.invoice_number}",
            DeliveryReceiptFormatter.LINE_WIDTH
        ))
        lines.append("")

        lines.append(EscposCommands.format_line(
            company_info.get('name', 'AYOP BIN ARSHAD'),
            DeliveryReceiptFormatter.LINE_WIDTH, 'center'
        ))
        lines.append(EscposCommands.format_line(
            company_info.get('address_1', ''),
            DeliveryReceiptFormatter.LINE_WIDTH, 'center'
        ))
        lines.append(EscposCommands.format_line(
            company_info.get('address_2', ''),
            DeliveryReceiptFormatter.LINE_WIDTH, 'center'
        ))
        lines.append("")

        # Company info
        company_reg = company_info.get('registration', '')
        company_phone = company_info.get('phone', '')
        invoice_date = delivery_invoice.invoice_date.strftime("%d/%m/%Y")
        lines.append(f"No Lesen     : {company_reg:<40} Tarikh : {invoice_date}")
        lines.append(f"No Telefon   : {company_phone}")
        lines.append("")

        # Truck info
        truck_number = delivery_invoice.truck.truck_number if delivery_invoice.truck else ""
        tare_weight = (
            float(delivery_invoice.truck.tare_weight)
            if delivery_invoice.truck and delivery_invoice.truck.tare_weight
            else 0
        )
        lines.append(f"NO LORI      : {truck_number}")
        lines.append(f"BERAT LORI   : {tare_weight:,.2f}")
        lines.append("")

        lines.append(EscposCommands.separator(DeliveryReceiptFormatter.LINE_WIDTH))
        lines.append("")

        # Destination
        mill_name = delivery_invoice.mill.mill_name if delivery_invoice.mill else "Unknown"
        lines.append("KEPADA:")
        lines.append(f"            {mill_name}")
        lines.append("")
        lines.append(f"                                              BERAT PADI    {float(delivery_invoice.total_weight):,.2f}")
        lines.append("")

        # Bill items header
        lines.append(EscposCommands.separator(DeliveryReceiptFormatter.LINE_WIDTH, '-'))
        lines.append("NO BIL  NAMA PESAWAH                      BERAT PADI  NO LORI   NAMA KILANG")
        lines.append(EscposCommands.separator(DeliveryReceiptFormatter.LINE_WIDTH, '-'))

        # Bill items
        for bill in bills:
            farmer_name = bill.farmer.name if bill.farmer else "Unknown"
            mill_code = delivery_invoice.mill.mill_code if delivery_invoice.mill else ""
            mill_short = delivery_invoice.mill.mill_name[:12] if delivery_invoice.mill else "KILANG"

            bill_line = (
                f"{bill.bill_number:<7} "
                f"{farmer_name:<35} "
                f"{float(bill.net_weight):>9,.0f} "
                f"{truck_number:<9} "
                f"{mill_short}"
            )
            lines.append(bill_line)

        # Footer
        lines.append(EscposCommands.separator(DeliveryReceiptFormatter.LINE_WIDTH, '-'))
        lines.append(
            f"                                    JUMLAH:   {float(delivery_invoice.total_weight):,.2f} kg"
        )
        lines.append(EscposCommands.separator(DeliveryReceiptFormatter.LINE_WIDTH))

        return '\n'.join(lines)
