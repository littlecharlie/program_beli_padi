"""
Calculation Service
Contains all business calculation logic for purchase bills and deliveries
"""
from decimal import Decimal, ROUND_HALF_UP


class CalculationService:
    """Service for all business calculations"""

    # Decimal precision for calculations
    PRECISION = Decimal('0.01')  # 2 decimal places

    @staticmethod
    def calculate_discount_weight(gross_weight: float, discount_percent: float) -> float:
        """
        Calculate discount weight based on gross weight and discount percentage

        Args:
            gross_weight: Gross weight in kg
            discount_percent: Discount percentage (0-100)

        Returns:
            Discount weight in kg (rounded to 2 decimal places)
        """
        gross = Decimal(str(gross_weight))
        percent = Decimal(str(discount_percent))
        result = (gross * percent / Decimal('100')).quantize(
            CalculationService.PRECISION,
            rounding=ROUND_HALF_UP
        )
        return float(result)

    @staticmethod
    def calculate_net_weight(gross_weight: float, discount_weight: float) -> float:
        """
        Calculate net weight

        Args:
            gross_weight: Gross weight in kg
            discount_weight: Discount weight in kg

        Returns:
            Net weight in kg (rounded to 2 decimal places)
        """
        gross = Decimal(str(gross_weight))
        discount = Decimal(str(discount_weight))
        result = (gross - discount).quantize(
            CalculationService.PRECISION,
            rounding=ROUND_HALF_UP
        )
        return float(result)

    @staticmethod
    def calculate_total_payment(net_weight: float, price_per_1000kg: float) -> float:
        """
        Calculate total payment based on net weight and price

        Args:
            net_weight: Net weight in kg
            price_per_1000kg: Price per 1000kg in RM

        Returns:
            Total payment in RM (rounded to 2 decimal places)
        """
        weight = Decimal(str(net_weight))
        price = Decimal(str(price_per_1000kg))
        result = (weight / Decimal('1000') * price).quantize(
            CalculationService.PRECISION,
            rounding=ROUND_HALF_UP
        )
        return float(result)

    @staticmethod
    def calculate_subsidy_estimate(net_weight: float, subsidy_rate: float = 0.50) -> float:
        """
        Calculate subsidy estimate

        Args:
            net_weight: Net weight in kg
            subsidy_rate: Subsidy rate per kg (default 0.50)

        Returns:
            Subsidy estimate in RM (rounded to 2 decimal places)
        """
        weight = Decimal(str(net_weight))
        rate = Decimal(str(subsidy_rate))
        result = (weight * rate).quantize(
            CalculationService.PRECISION,
            rounding=ROUND_HALF_UP
        )
        return float(result)

    @staticmethod
    def calculate_total_discount_percent(wap_basah: float, hampa_padi: float,
                                        padi_muda: float) -> float:
        """
        Calculate total discount percentage by adding individual discounts

        Args:
            wap_basah: Moisture discount %
            hampa_padi: Empty grains discount %
            padi_muda: Damaged rice discount %

        Returns:
            Total discount percentage (rounded to 2 decimal places)
        """
        total = Decimal(str(wap_basah)) + Decimal(str(hampa_padi)) + Decimal(str(padi_muda))
        result = total.quantize(
            CalculationService.PRECISION,
            rounding=ROUND_HALF_UP
        )
        return float(result)

    @staticmethod
    def calculate_purchase_bill(gross_weight: float,
                               discount_wap_basah: float,
                               discount_hampa_padi: float,
                               discount_padi_muda: float,
                               rice_price: float,
                               subsidy_rate: float = 0.50) -> dict:
        """
        Complete purchase bill calculation

        Args:
            gross_weight: Gross weight in kg
            discount_wap_basah: Moisture discount %
            discount_hampa_padi: Empty grains discount %
            discount_padi_muda: Damaged rice discount %
            rice_price: Price per 1000kg
            subsidy_rate: Subsidy rate per kg

        Returns:
            Dictionary with all calculated values:
            {
                'total_discount_percent': float,
                'discount_weight': float,
                'net_weight': float,
                'total_payment': float,
                'subsidy_estimate': float
            }
        """
        # Calculate total discount percentage
        total_discount_percent = CalculationService.calculate_total_discount_percent(
            discount_wap_basah, discount_hampa_padi, discount_padi_muda
        )

        # Calculate discount weight
        discount_weight = CalculationService.calculate_discount_weight(
            gross_weight, total_discount_percent
        )

        # Calculate net weight
        net_weight = CalculationService.calculate_net_weight(gross_weight, discount_weight)

        # Calculate total payment
        total_payment = CalculationService.calculate_total_payment(net_weight, rice_price)

        # Calculate subsidy estimate
        subsidy_estimate = CalculationService.calculate_subsidy_estimate(net_weight, subsidy_rate)

        return {
            'total_discount_percent': total_discount_percent,
            'discount_weight': discount_weight,
            'net_weight': net_weight,
            'total_payment': total_payment,
            'subsidy_estimate': subsidy_estimate
        }

    @staticmethod
    def calculate_delivery_total_weight(purchase_bills: list) -> float:
        """
        Calculate total weight for delivery invoice

        Args:
            purchase_bills: List of purchase bill objects with net_weight attribute

        Returns:
            Total net weight in kg (rounded to 2 decimal places)
        """
        if not purchase_bills:
            return 0.0

        total = Decimal('0')
        for bill in purchase_bills:
            total += Decimal(str(bill.net_weight))

        result = total.quantize(
            CalculationService.PRECISION,
            rounding=ROUND_HALF_UP
        )
        return float(result)

    @staticmethod
    def validate_total_discount(wap_basah: float, hampa_padi: float,
                               padi_muda: float) -> tuple[bool, str]:
        """
        Validate that total discount does not exceed 100%

        Args:
            wap_basah: Moisture discount %
            hampa_padi: Empty grains discount %
            padi_muda: Damaged rice discount %

        Returns:
            (is_valid, error_message)
        """
        total = CalculationService.calculate_total_discount_percent(
            wap_basah, hampa_padi, padi_muda
        )

        if total > 100:
            return False, f"Total discount ({total}%) cannot exceed 100%"

        return True, ""
