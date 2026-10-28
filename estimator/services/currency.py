import re
from decimal import Decimal, InvalidOperation

def convert_currency(amount, from_currency, to_currency, exchange_rate):                # Function to convert an amount between two currencies
    
    # Validate currency codes
    if not isinstance(from_currency, str) or not isinstance(to_currency, str):
        raise ValueError("Currency codes must be strings.")

    source = from_currency.strip().upper()
    target = to_currency.strip().upper()

    if not re.fullmatch(r"[A-Z]{3}", source):
        raise ValueError("Invalid source currency code.")

    if not re.fullmatch(r"[A-Z]{3}", target):
        raise ValueError("Invalid target currency code.")

    if source not in SUPPORTED_CURRENCIES:
        raise ValueError("Unsupported source currency.")

    if target not in SUPPORTED_CURRENCIES:
        raise ValueError("Unsupported target currency.")

    # Convert inputs to Decimal and validate numbers
    try:
        value = Decimal(str(amount))
        rate = Decimal(str(exchange_rate))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Amount and exchange rate must be valid numbers.") from exc

    if not value.is_finite() or not rate.is_finite():
        raise ValueError("Amount and exchange rate must be finite numbers.")

    # Validate exchange rate
    if rate <= 0:
        raise ValueError("Exchange rate must be greater than zero.")

    # Handle identical currencies
    if source == target:
        if rate != Decimal("1"):
            raise ValueError("Exchange rate must be 1 for identical currencies.")
        return value

    # Convert and return the amount
    converted_amount = value / rate

    return converted_amount

SUPPORTED_CURRENCIES = {
    "CHF", "GBP", "USD", "EUR", "INR",
    "AED", "SAR", "CAD", "AUD", "JPY"
}