"""
Enhanced Purchase Receipt Formatter
Generates receipts matching the sample PDF format exactly
"""
from typing import Dict, Any
from printing.layout_utils import ReceiptLayoutUtils
from printing.malay_labels import MalayLabels


class PurchaseReceiptFormatter:
    """
    Enhanced purchase receipt formatter for Epson LQ-310
    Generates text output with precise alignment matching sample PDF
    """

    @staticmethod
    def format_receipt(receipt_data: Dict[str, Any]) -> str:
        """
        Generate formatted purchase receipt from structured data

        Args:
            receipt_data: Dictionary from ReceiptDataService.prepare_purchase_bill_data()

        Returns:
            Formatted receipt string ready for printing
        """
        lines = []

        # ===== HEADER SECTION =====
        # Top left: "SUBSIDI PADI" (not centered)
        lines.append(MalayLabels.HEADER_SUBSIDI_PADI)
        # Title and company name (centered)
        lines.append(ReceiptLayoutUtils.center_text(MalayLabels.TITLE_BIL_BELIAN))
        lines.append(ReceiptLayoutUtils.center_text(receipt_data['company']['name']))
        lines.append(ReceiptLayoutUtils.center_text(receipt_data['company']['address_line1']))
        lines.append(ReceiptLayoutUtils.center_text(receipt_data['company']['address_line2']))
        lines.append(ReceiptLayoutUtils.center_text(receipt_data['company']['address_line3']))

        # License and phone in two columns
        lines.append(ReceiptLayoutUtils.format_two_columns(
            MalayLabels.LICENSE_NUMBER, receipt_data['company']['registration'],
            MalayLabels.BILL_NUMBER, receipt_data['transaction']['bill_number']
        ))
        lines.append(ReceiptLayoutUtils.format_two_columns(
            MalayLabels.PHONE_NUMBER, receipt_data['company']['phone'],
            "", ""
        ))
        lines.append(ReceiptLayoutUtils.separator_line('='))

        # ===== FARMER INFORMATION SECTION =====
        # Name and date on same line
        farmer_name = f"{MalayLabels.FARMER_NAME} : {receipt_data['farmer']['name']}"
        date_part = f"{MalayLabels.DATE}:  {receipt_data['transaction']['bill_date']}"
        spacing = 80 - len(farmer_name) - len(date_part)
        lines.append(f"{farmer_name}{' ' * spacing}{date_part}")

        # Address
        lines.append(ReceiptLayoutUtils.format_label_value(
            MalayLabels.ADDRESS,
            receipt_data['farmer']['address'],
            label_width=20,
            total_width=80
        ))

        # Registration numbers (two columns)
        left_reg = f"{MalayLabels.FARMER_REGISTRATION} : {receipt_data['farmer']['registration']}"
        right_subsidy = f"{MalayLabels.SUBSIDY_CARD}: {receipt_data['farmer']['subsidy_code']}"
        spacing = 80 - len(left_reg) - len(right_subsidy)
        lines.append(f"{left_reg}{' ' * spacing}{right_subsidy}")

        # IC and truck number on same line
        ic_part = f"{MalayLabels.IC_NUMBER} : {receipt_data['farmer']['ic_number']}"
        truck_part = f"{MalayLabels.TRUCK_NUMBER}: {receipt_data['transaction']['truck_number']}"
        spacing = 80 - len(ic_part) - len(truck_part)
        lines.append(f"{ic_part}{' ' * spacing}{truck_part}")

        # Bank account and weighbridge receipt on same line
        bank_part = f"{MalayLabels.BANK_ACCOUNT} : {receipt_data['farmer']['bank_account']}"
        weighbridge_part = f"{MalayLabels.WEIGHBRIDGE_RECEIPT}: {receipt_data['transaction']['weighbridge_receipt']}"
        spacing = 80 - len(bank_part) - len(weighbridge_part)
        lines.append(f"{bank_part}{' ' * spacing}{weighbridge_part}")

        # ===== DISCOUNT SECTION =====
        lines.append(ReceiptLayoutUtils.separator_line('-'))
        lines.append(ReceiptLayoutUtils.format_discount_line(
            receipt_data['discounts']['wap_basah'],
            receipt_data['discounts']['hampa_padi'],
            receipt_data['discounts']['padi_muda'],
            receipt_data['discounts']['total_percent']
        ))
        lines.append(ReceiptLayoutUtils.separator_line('-'))

        # ===== WEIGHT AND PAYMENT TABLE =====
        # Table structure from sample PDF with dashed lines
        col_widths = [20, 18, 17, 14, 11]
        header_cols = [
            MalayLabels.GROSS_WEIGHT,
            f"(-) {MalayLabels.DISCOUNT}",
            MalayLabels.NET_WEIGHT,
            MalayLabels.PRICE_1000KG,
            MalayLabels.RICE_VALUE
        ]

        lines.append(ReceiptLayoutUtils.separator_line('-'))
        lines.append(ReceiptLayoutUtils.format_columns(header_cols, col_widths, ['left'] * 5))
        lines.append(ReceiptLayoutUtils.format_columns(
            ["(KG)", "", "(KG)", "", ""],
            col_widths,
            ['left'] * 5
        ))
        lines.append(ReceiptLayoutUtils.separator_line('-'))

        # Data row - all values right-aligned
        data_cols = [
            ReceiptLayoutUtils.format_weight(receipt_data['calculations']['gross_weight']),
            ReceiptLayoutUtils.format_weight(receipt_data['calculations']['discount_weight']),
            ReceiptLayoutUtils.format_weight(receipt_data['calculations']['net_weight']),
            ReceiptLayoutUtils.format_money(receipt_data['calculations']['rice_price']),
            ReceiptLayoutUtils.format_money(receipt_data['calculations']['total_payment'])
        ]
        lines.append(ReceiptLayoutUtils.format_columns(data_cols, col_widths, ['right'] * 5))
        lines.append(ReceiptLayoutUtils.separator_line('='))

        # ===== SUBSIDY AND SUMMARY =====
        subsidy_value = ReceiptLayoutUtils.format_weight(
            receipt_data['calculations']['subsidy_estimate']
        )
        lines.append(f"{MalayLabels.SUBSIDY_ESTIMATE:<35} {subsidy_value:>45}")

        # Harvest area and total payment
        lines.append(f"{MalayLabels.HARVEST_AREA} : {receipt_data['transaction']['harvest_area']}")
        lines.append(f"{MalayLabels.TOTAL_PAYMENT:<35} {ReceiptLayoutUtils.format_money(receipt_data['calculations']['total_payment']):>45}")

        # ===== FOOTER SECTION =====
        lines.append(ReceiptLayoutUtils.separator_line('-'))

        # Signature labels on same line
        footer_line = f"{MalayLabels.PREPARED_BY:<40}{MalayLabels.RECEIVER_SIGNATURE}"
        lines.append(footer_line)

        # Add 3 blank lines for spacing before dashes (reduced from 5)
        lines.append("")
        lines.append("")
        lines.append("")

        # Dashed signature lines (10 dashes each, aligned under labels)
        signature_dashes = "-" * 10
        dashes_line = f"{signature_dashes:<40}{signature_dashes}"
        lines.append(dashes_line)

        return '\n'.join(lines)

    @staticmethod
    def format_receipt_for_printing(receipt_data: Dict[str, Any]) -> str:
        """
        Generate formatted receipt with ESC/P commands for printer

        Args:
            receipt_data: Dictionary from ReceiptDataService.prepare_purchase_bill_data()

        Returns:
            Formatted receipt with ESC/P commands
        """
        from printing.escpos_commands import EscposCommands

        # Generate base receipt
        receipt = PurchaseReceiptFormatter.format_receipt(receipt_data)

        # Add printer initialization and formatting commands
        output = []
        output.append(EscposCommands.INIT_PRINTER)
        output.append(EscposCommands.PICA_10CPI)
        output.append(EscposCommands.LINE_SPACING_6)
        output.append(receipt)
        output.append(EscposCommands.FORM_FEED)

        return ''.join(output)
