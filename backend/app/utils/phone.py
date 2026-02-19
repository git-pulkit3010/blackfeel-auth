# backend/app/utils/phone.py
import phonenumbers
from phonenumbers import NumberParseException
from typing import Optional

def format_phone_number(phone_number: str, default_region: str = "IN") -> str:
    """
    Format phone number to international format (E.164)
    Args:
        phone_number: Raw phone number input
        default_region: Default region to use if none provided (e.g., 'IN' for India)
    Returns:
        Formatted phone number in E.164 format (e.g., +9188827...)
    """
    if not phone_number:
        return phone_number

    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone_number, default_region)
        
        # Check if the number is valid
        if phonenumbers.is_valid_number(parsed_number):
            # Return in E.164 format but remove the leading +
            formatted = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            return formatted.lstrip('+')
        else:
            # If invalid, return original number without +
            return phone_number.lstrip('+')
    except NumberParseException:
        # If parsing fails, return original number without +
        return phone_number.lstrip('+')


def is_valid_phone_number(phone_number: str, default_region: str = "IN") -> bool:
    """
    Validate phone number format
    Args:
        phone_number: Phone number to validate
        default_region: Default region to use for validation (e.g., 'IN' for India)
    Returns:
        Boolean indicating if the phone number is valid
    """
    if not phone_number:
        return False

    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone_number, default_region)
        
        # Check if the number is valid
        return phonenumbers.is_valid_number(parsed_number)
    except NumberParseException:
        return False