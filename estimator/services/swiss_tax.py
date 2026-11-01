from decimal import Decimal, InvalidOperation


# Calculate total Swiss tax including the personal tax
def swiss_incometax(federal, cantonal, communal, personal=0):
    try:
        taxes = [
            Decimal(str(value))
            for value in (federal, cantonal, communal, personal)
        ]
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid Swiss tax amount.")

    if any(not tax.is_finite() or tax < 0 for tax in taxes):
        raise ValueError("Swiss tax amounts must be finite and non-negative.")

    return sum(taxes, Decimal("0"))