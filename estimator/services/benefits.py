from decimal import Decimal, InvalidOperation
from .currency import convert_currency

RELOCATION_LIMIT = Decimal("8000")


# Calculate tax relief for qualifying relocation expenses
def relocation_relief(moving, temporary, moving_ok=False, temporary_ok=False):
    try:
        moving_cost = Decimal(str(moving))
        temporary_cost = Decimal(str(temporary))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid relocation expense.")

    if any(not cost.is_finite() or cost < 0 for cost in (moving_cost, temporary_cost)):
        raise ValueError("Relocation expenses must be finite and non-negative.")

    if not isinstance(moving_ok, bool) or not isinstance(temporary_ok, bool):
        raise ValueError("Eligibility must be True or False.")

    qualifying = (
        (moving_cost if moving_ok else Decimal("0"))
        + (temporary_cost if temporary_ok else Decimal("0"))
    )

    exempt = min(qualifying, RELOCATION_LIMIT)
    total = moving_cost + temporary_cost

    return {
        "total": total,
        "qualifying": qualifying,
        "exempt": exempt,
        "non_exempt": total - exempt
    }

# Calculate employer housing expenditure
def housing_cost(monthly_rent, months=12):
    try:
        rent = Decimal(str(monthly_rent))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid monthly rent.")

    if not rent.is_finite() or rent < 0:
        raise ValueError("Monthly rent must be finite and non-negative.")

    if isinstance(months, bool) or not isinstance(months, int) or months < 0:
        raise ValueError("Months must be a non-negative integer.")

    return rent * months

# Calculate taxable housing benefit after eligible relief
def housing_tax(gross_value, relief=0):
    try:
        gross = Decimal(str(gross_value))
        deduction = Decimal(str(relief))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid housing benefit amount.")

    if not gross.is_finite() or not deduction.is_finite():
        raise ValueError("Housing amounts must be finite.")

    if gross < 0 or deduction < 0:
        raise ValueError("Housing amounts cannot be negative.")

    if deduction > gross:
        raise ValueError("Relief cannot exceed the gross benefit.")

    return {
        "gross": gross,
        "relief": deduction,
        "taxable": gross - deduction
    }

# Convert a cash relocation allowance into GBP
def relocation_cash(amount, currency, exchange_rate):
    value = convert_currency(amount, currency, "GBP", exchange_rate)

    if value < 0:
        raise ValueError("Relocation allowance cannot be negative.")

    return {
        "cost": value,
        "taxable_cash": value
    }
