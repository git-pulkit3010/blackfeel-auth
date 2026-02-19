# Test script to verify phone number formatting and validation
import sys
sys.path.append('/home/pulkit3010/BlackFeel/blackfeel-signin-security/backend')

from app.utils.phone import format_phone_number, is_valid_phone_number

# Test cases
test_numbers = [
    "+918882712711",  # Valid international format
    "918882712711",   # Without +
    "8882712711",     # 10-digit Indian number without country code
    "98882712711",    # 11-digit with country code without +
    "+1234567890",    # US number
    "invalid",        # Invalid
    "",               # Empty
    "+91000000000",   # Invalid Indian number (all zeros after code)
]

print("Testing phone number utilities:")
for number in test_numbers:
    formatted = format_phone_number(number)
    is_valid = is_valid_phone_number(number)
    print(f"Input: '{number}' -> Formatted: '{formatted}', Valid: {is_valid}")