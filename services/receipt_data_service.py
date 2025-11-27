"""
Receipt Data Service
Prepares structured data for receipt generation
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.purchase_bill import PurchaseBill
from models.delivery_invoice import DeliveryInvoice
from services.config_service import ConfigService


class ReceiptDataService:
    """Prepare structured data for receipt generation"""

    @staticmethod
    def prepare_purchase_bill_data(
        db: Session,
        purchase_bill: PurchaseBill
    ) -> Dict[str, Any]:
        """
        Prepare complete data structure for purchase bill receipt

        Args:
            db: Database session
            purchase_bill: PurchaseBill object

        Returns:
            Dictionary with all required fields properly formatted
        """
        # Company info from config
        company_data = {
            'name': ConfigService.get_value(db, 'company_name', 'AYOP BIN ARSHAD'),
            'address_line1': 'LOT 49, PARIT 10, PASIR PANJANG,',
            'address_line2': '45400 SEKINCHAN, SELANGOR',
            'address_line3': 'SELANGOR DARUL EHSAN.',
            'registration': ConfigService.get_value(db, 'company_registration', '474523-K'),
            'phone': ConfigService.get_value(db, 'company_phone', '0162120051')
        }

        # Farmer data with proper fallbacks
        farmer = purchase_bill.farmer
        farmer_data = {
            'name': farmer.name if farmer else '',
            'ic_number': farmer.ic_number if farmer else '',
            'address': farmer.address if farmer and farmer.address else '0',
            'registration': farmer.registration_number if farmer and farmer.registration_number else '0',
            'subsidy_code': farmer.subsidy_code if farmer and farmer.subsidy_code else '0',
            'bank_account': farmer.bank_account if farmer and farmer.bank_account else '0'
        }

        # Transaction metadata
        transaction_data = {
            'bill_number': purchase_bill.bill_number,
            'bill_date': purchase_bill.bill_date.strftime("%d/%m/%Y %H:%M"),
            'truck_number': purchase_bill.truck.truck_number if purchase_bill.truck else '',
            'weighbridge_receipt': purchase_bill.weighbridge_receipt or '0',
            'harvest_area': purchase_bill.harvest_area.area_name if purchase_bill.harvest_area else ''
        }

        # Discount breakdown
        discount_data = {
            'wap_basah': float(purchase_bill.discount_wap_basah),
            'hampa_padi': float(purchase_bill.discount_hampa_padi),
            'padi_muda': float(purchase_bill.discount_padi_muda),
            'total_percent': float(purchase_bill.total_discount_percent)
        }

        # Weight and payment calculations
        calculation_data = {
            'gross_weight': float(purchase_bill.gross_weight),
            'discount_weight': float(purchase_bill.discount_weight),
            'net_weight': float(purchase_bill.net_weight),
            'rice_price': float(purchase_bill.rice_price_per_1000kg),
            'total_payment': float(purchase_bill.total_payment),
            'subsidy_estimate': float(purchase_bill.subsidy_estimate)
        }

        return {
            'company': company_data,
            'farmer': farmer_data,
            'transaction': transaction_data,
            'discounts': discount_data,
            'calculations': calculation_data
        }

    @staticmethod
    def prepare_delivery_invoice_data(
        db: Session,
        delivery_invoice: DeliveryInvoice
    ) -> Dict[str, Any]:
        """
        Prepare complete data structure for delivery invoice receipt

        Args:
            db: Database session
            delivery_invoice: DeliveryInvoice object

        Returns:
            Dictionary with all required fields
        """
        # Company info
        company_data = {
            'name': ConfigService.get_value(db, 'company_name', 'AYOP BIN ARSHAD'),
            'address_line1': 'LOT 49, PARIT 10, PASIR PANJANG,',
            'address_line2': '45400 SEKINCHAN, SELANGOR',
            'address_line3': 'SELANGOR DARUL EHSAN.',
            'registration': ConfigService.get_value(db, 'company_registration', '474523-K'),
            'phone': ConfigService.get_value(db, 'company_phone', '0162120051')
        }

        # Rice mill data
        rice_mill = delivery_invoice.rice_mill
        mill_data = {
            'name': rice_mill.mill_name if rice_mill else '',
            'address': rice_mill.address if rice_mill and rice_mill.address else '0',
            'contact': rice_mill.contact_person if rice_mill and rice_mill.contact_person else '0'
        }

        # Truck data
        truck = delivery_invoice.truck
        truck_data = {
            'number': truck.truck_number if truck else '',
            'driver': truck.driver_name if truck and truck.driver_name else '',
            'contact': truck.driver_contact if truck and truck.driver_contact else ''
        }

        # Transaction metadata
        transaction_data = {
            'invoice_number': delivery_invoice.invoice_number,
            'invoice_date': delivery_invoice.invoice_date.strftime("%d/%m/%Y %H:%M"),
            'bill_count': len(delivery_invoice.purchase_bills) if delivery_invoice.purchase_bills else 0
        }

        # Calculate totals from associated bills
        total_weight = sum(float(bill.net_weight) for bill in delivery_invoice.purchase_bills) if delivery_invoice.purchase_bills else 0.0
        total_payment = sum(float(bill.total_payment) for bill in delivery_invoice.purchase_bills) if delivery_invoice.purchase_bills else 0.0

        calculation_data = {
            'total_weight': total_weight,
            'total_payment': total_payment,
            'bill_numbers': [bill.bill_number for bill in delivery_invoice.purchase_bills] if delivery_invoice.purchase_bills else []
        }

        return {
            'company': company_data,
            'rice_mill': mill_data,
            'truck': truck_data,
            'transaction': transaction_data,
            'calculations': calculation_data
        }
