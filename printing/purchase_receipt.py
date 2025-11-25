"""
Purchase Receipt Formatter
Formats purchase bills for printing on Epson LQ-310
"""
import os
from datetime import datetime
from printing.escpos_commands import EscposCommands


class PurchaseReceiptFormatter:
    """Format purchase bills for printing"""

    LINE_WIDTH = 80

    @staticmethod
    def load_template() -> str:
        """Load purchase template from file"""
        template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'purchase_template.txt'
        )

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    @staticmethod
    def format_receipt(purchase_bill, company_info: dict) -> str:
        """
        Format purchase bill receipt

        Args:
            purchase_bill: PurchaseBill model object
            company_info: Dictionary with company information

        Returns:
            Formatted receipt string
        """
        template = PurchaseReceiptFormatter.load_template()

        if not template:
            return PurchaseReceiptFormatter.generate_receipt(purchase_bill, company_info)

        # Format bill date
        bill_date = purchase_bill.bill_date.strftime("%d/%m/%Y %H:%M")

        # Get farmer info
        farmer_address = purchase_bill.farmer.address if purchase_bill.farmer else ""
        farmer_registration = purchase_bill.farmer.registration_number if purchase_bill.farmer else ""
        farmer_subsidy_code = purchase_bill.farmer.subsidy_code if purchase_bill.farmer else ""
        farmer_ic = purchase_bill.farmer.ic_number if purchase_bill.farmer else ""
        farmer_name = purchase_bill.farmer.name if purchase_bill.farmer else ""
        farmer_bank_account = purchase_bill.farmer.bank_account if purchase_bill.farmer else ""

        # Get truck info
        truck_number = purchase_bill.truck.truck_number if purchase_bill.truck else ""

        # Get harvest area
        harvest_area = purchase_bill.harvest_area.area_name if purchase_bill.harvest_area else ""

        # Replace placeholders
        receipt = template.format(
            company_name=company_info.get('name', ''),
            company_address_1=company_info.get('address_1', ''),
            company_address_2=company_info.get('address_2', ''),
            company_registration=company_info.get('registration', ''),
            company_phone=company_info.get('phone', ''),
            bill_number=purchase_bill.bill_number,
            bill_date=bill_date,
            farmer_name=farmer_name,
            farmer_address=farmer_address or '0',
            farmer_registration=farmer_registration or '0',
            farmer_subsidy_code=farmer_subsidy_code or '0',
            farmer_ic=farmer_ic,
            farmer_bank_account=farmer_bank_account or '0',
            truck_number=truck_number,
            weighbridge_receipt=purchase_bill.weighbridge_receipt or '0',
            discount_wap_basah=f"{float(purchase_bill.discount_wap_basah):.2f}",
            discount_hampa_padi=f"{float(purchase_bill.discount_hampa_padi):.2f}",
            discount_padi_muda=f"{float(purchase_bill.discount_padi_muda):.2f}",
            total_discount_percent=f"{float(purchase_bill.total_discount_percent):.2f}",
            gross_weight=f"{float(purchase_bill.gross_weight):,.2f}",
            discount_weight=f"{float(purchase_bill.discount_weight):,.2f}",
            net_weight=f"{float(purchase_bill.net_weight):,.2f}",
            rice_price_per_1000kg=f"{float(purchase_bill.rice_price_per_1000kg):,.2f}",
            total_payment=f"{float(purchase_bill.total_payment):,.2f}",
            subsidy_estimate=f"{float(purchase_bill.subsidy_estimate):,.2f}",
            harvest_area=harvest_area
        )

        return receipt

    @staticmethod
    def generate_receipt(purchase_bill, company_info: dict) -> str:
        """
        Generate receipt manually if template not available

        Args:
            purchase_bill: PurchaseBill model object
            company_info: Dictionary with company information

        Returns:
            Formatted receipt string
        """
        lines = []

        # Header
        lines.append(EscposCommands.separator(PurchaseReceiptFormatter.LINE_WIDTH))
        lines.append(EscposCommands.format_line(company_info.get('name', 'AYOP BIN ARSHAD'),
                                               PurchaseReceiptFormatter.LINE_WIDTH, 'center'))
        lines.append(EscposCommands.format_line(company_info.get('address_1', ''),
                                               PurchaseReceiptFormatter.LINE_WIDTH, 'center'))
        lines.append(EscposCommands.format_line(company_info.get('address_2', ''),
                                               PurchaseReceiptFormatter.LINE_WIDTH, 'center'))
        lines.append("")

        # Company info line
        company_reg = company_info.get('registration', '')
        company_phone = company_info.get('phone', '')
        lines.append(f"NO LESEN: {company_reg:<45} NO. TELEFON: {company_phone}")

        lines.append(EscposCommands.separator(PurchaseReceiptFormatter.LINE_WIDTH))
        lines.append("")

        # Bill title
        lines.append(EscposCommands.format_line(f"BIL BELIAN : {purchase_bill.bill_number}",
                                               PurchaseReceiptFormatter.LINE_WIDTH, 'center'))
        lines.append("")

        # Farmer info
        bill_date = purchase_bill.bill_date.strftime("%d/%m/%Y %H:%M")
        farmer_name = purchase_bill.farmer.name if purchase_bill.farmer else ""
        farmer_address = purchase_bill.farmer.address if purchase_bill.farmer else "0"
        lines.append(f"NAMA PETANI  : {farmer_name:<30} TARIKH: {bill_date}")
        lines.append(f"ALAMAT       : {farmer_address}")
        lines.append("")

        # Additional farmer info
        farmer_reg = purchase_bill.farmer.registration_number if purchase_bill.farmer else "0"
        farmer_subsidy = purchase_bill.farmer.subsidy_code if purchase_bill.farmer else "0"
        farmer_ic = purchase_bill.farmer.ic_number if purchase_bill.farmer else ""
        farmer_bank = purchase_bill.farmer.bank_account if purchase_bill.farmer else "0"
        truck_number = purchase_bill.truck.truck_number if purchase_bill.truck else ""
        weighbridge = purchase_bill.weighbridge_receipt or "0"

        lines.append(f"NO DAFTAR PESAWAH: {farmer_reg}")
        lines.append(f"NO KAD SUBSIDI   : {farmer_subsidy}")
        lines.append(f"NO KAD PENGENALAN: {farmer_ic:<25} NO LORI: {truck_number}")
        lines.append(f"NO AKAUN BANK    : {farmer_bank:<30} NO RESIT TIMBANG: {weighbridge}")
        lines.append("")

        # Discounts
        lines.append(EscposCommands.separator(PurchaseReceiptFormatter.LINE_WIDTH, '-'))
        discount_line = (f"Wap Basah: {float(purchase_bill.discount_wap_basah):>5.2f}  "
                        f"Hampa Padi: {float(purchase_bill.discount_hampa_padi):>5.2f}  "
                        f"Padi Muda/Rosak: {float(purchase_bill.discount_padi_muda):>5.2f}  "
                        f"= {float(purchase_bill.total_discount_percent):>5.2f}%")
        lines.append(discount_line)
        lines.append(EscposCommands.separator(PurchaseReceiptFormatter.LINE_WIDTH, '-'))
        lines.append("")

        # Calculations
        lines.append(f"BERAT TIMBANGAN (KG)         : {float(purchase_bill.gross_weight):>10,.2f}")
        lines.append(f"(-) POTONGAN                 : {float(purchase_bill.discount_weight):>10,.2f}")
        lines.append(f"BERAT BERSIH (KG)            : {float(purchase_bill.net_weight):>10,.2f}")
        lines.append(f"HARGA (1000KG)               : RM {float(purchase_bill.rice_price_per_1000kg):>10,.2f}")
        lines.append(f"NILAI PADI                   : RM {float(purchase_bill.total_payment):>10,.2f}")
        lines.append("")

        lines.append(f"Anggaran Subsidi             : {float(purchase_bill.subsidy_estimate):>10,.2f}")
        lines.append("")

        # Summary
        harvest_area = purchase_bill.harvest_area.area_name if purchase_bill.harvest_area else ""
        lines.append(f"KAWASAN TUAIAN               : {harvest_area}")
        lines.append(f"JUMLAH BAYARAN               : RM {float(purchase_bill.total_payment):>10,.2f}")
        lines.append("")

        # Footer
        lines.append(EscposCommands.separator(PurchaseReceiptFormatter.LINE_WIDTH))
        lines.append("DISEDIAKAN OLEH                              T. TANGAN PENERIMA")
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append("")
        lines.append(EscposCommands.separator(PurchaseReceiptFormatter.LINE_WIDTH, '_'))
        lines.append("SUBSIDI PADI")
        lines.append(EscposCommands.format_line("BIL BELIAN PADI",
                                               PurchaseReceiptFormatter.LINE_WIDTH, 'center'))
        lines.append(EscposCommands.format_line(company_info.get('name', ''),
                                               PurchaseReceiptFormatter.LINE_WIDTH, 'center'))
        lines.append(EscposCommands.format_line(company_info.get('address_1', ''),
                                               PurchaseReceiptFormatter.LINE_WIDTH, 'center'))
        lines.append(EscposCommands.separator(PurchaseReceiptFormatter.LINE_WIDTH))

        return '\n'.join(lines)
