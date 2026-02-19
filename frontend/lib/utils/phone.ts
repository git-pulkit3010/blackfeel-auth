/**
 * Format phone number to international format (E.164)
 * @param phoneNumber - Raw phone number input
 * @param defaultCountryCode - Default country code to use if none provided (e.g., '91' for India)
 * @returns Formatted phone number in E.164 format (e.g., +9188827...)
 */
export function formatPhoneNumber(phoneNumber: string, defaultCountryCode: string = '91'): string {
  if (!phoneNumber) return phoneNumber;

  // Remove all non-digit characters except +
  let cleaned = phoneNumber.replace(/[^\d+]/g, '');

  // If it's already in international format or just a +, let it be
  if (cleaned.startsWith('+')) {
    return cleaned;
  }

  // Handle local Indian format with leading 0 (e.g., 08882712345 -> +918882712345)
  if (cleaned.startsWith('0') && cleaned.length === 11) {
    return '+' + defaultCountryCode + cleaned.substring(1);
  }

  // Handle 10-digit Indian mobile numbers (starting with 6-9)
  if (cleaned.length === 10 && /^[6-9]/.test(cleaned)) {
    return '+' + defaultCountryCode + cleaned;
  }

  // Handle 12-digit Indian numbers already starting with 91 (e.g., 918882712345 -> +918882712345)
  if (cleaned.startsWith(defaultCountryCode) && cleaned.length === 12) {
    return '+' + cleaned;
  }

  // For other cases, just return cleaned digits and let the user finish typing
  // Validation will happen on submit
  return cleaned;
}

/**
 * Validate phone number format
 * @param phoneNumber - Phone number to validate
 * @returns boolean indicating if the phone number is valid
 */
export function isValidPhoneNumber(phoneNumber: string): boolean {
  if (!phoneNumber) return false;

  // Check if it matches E.164 format: + followed by 1-15 digits
  // The first digit after + cannot be 0
  const e164Regex = /^\+[1-9]\d{6,14}$/;
  
  return e164Regex.test(phoneNumber);
}