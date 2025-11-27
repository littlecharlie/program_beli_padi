"""
Validation Rules
Input validation for all user inputs
"""
import re
from datetime import datetime
from decimal import Decimal
from typing import Tuple


class Validators:
    """Input validation class"""

    @staticmethod
    def validate_ic_number(ic: str) -> Tuple[bool, str]:
        """
        Validate Malaysian IC number (12 digits)

        Returns:
            (is_valid, error_message)
        """
        if not ic:
            return False, "IC number is required"

        ic_clean = re.sub(r'[\s-]', '', ic)

        if not ic_clean.isdigit():
            return False, "IC number must contain only digits"

        if len(ic_clean) != 12:
            return False, "IC number must be 12 digits"

        return True, ""

    @staticmethod
    def validate_weight(weight, field_name: str = "Weight") -> Tuple[bool, str]:
        """
        Validate weight value

        Returns:
            (is_valid, error_message)
        """
        if weight is None or weight == '':
            return False, f"{field_name} is required"

        try:
            weight_val = float(weight)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a number"

        if weight_val <= 0:
            return False, f"{field_name} must be greater than 0"

        if weight_val > 1000000:
            return False, f"{field_name} is too large"

        return True, ""

    @staticmethod
    def validate_percentage(percent, field_name: str = "Percentage") -> Tuple[bool, str]:
        """
        Validate percentage value (0-100)

        Returns:
            (is_valid, error_message)
        """
        if percent is None or percent == '':
            return False, f"{field_name} is required"

        try:
            percent_val = float(percent)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a number"

        if percent_val < 0 or percent_val > 100:
            return False, f"{field_name} must be between 0 and 100"

        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate Malaysian phone number

        Returns:
            (is_valid, error_message)
        """
        if not phone or phone == '':
            return True, ""  # Phone is optional

        phone_clean = re.sub(r'[\s-]', '', phone)

        if not re.match(r'^0\d{8,10}$', phone_clean):
            return False, "Invalid phone number format"

        return True, ""

    @staticmethod
    def validate_truck_number(truck_number: str) -> Tuple[bool, str]:
        """
        Validate truck number

        Returns:
            (is_valid, error_message)
        """
        if not truck_number or truck_number == '':
            return False, "Truck number is required"

        if len(truck_number.strip()) < 2:
            return False, "Truck number is too short"

        if len(truck_number) > 20:
            return False, "Truck number is too long"

        return True, ""

    @staticmethod
    def validate_date(date: datetime) -> Tuple[bool, str]:
        """
        Validate date (cannot be future)

        Returns:
            (is_valid, error_message)
        """
        if not date:
            return False, "Date is required"

        if date > datetime.now():
            return False, "Date cannot be in the future"

        return True, ""

    @staticmethod
    def validate_required_field(value, field_name: str) -> Tuple[bool, str]:
        """
        Validate required field

        Returns:
            (is_valid, error_message)
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{field_name} is required"

        return True, ""

    @staticmethod
    def validate_decimal(value, field_name: str = "Value", min_val=None, max_val=None) -> Tuple[bool, str]:
        """
        Validate decimal value

        Returns:
            (is_valid, error_message)
        """
        if value is None or value == '':
            return False, f"{field_name} is required"

        try:
            val = Decimal(str(value))
        except:
            return False, f"{field_name} must be a valid number"

        if min_val is not None and val < Decimal(str(min_val)):
            return False, f"{field_name} must be at least {min_val}"

        if max_val is not None and val > Decimal(str(max_val)):
            return False, f"{field_name} must not exceed {max_val}"

        return True, ""
