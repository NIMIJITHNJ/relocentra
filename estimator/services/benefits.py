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

# Split relocation expenses into exempt and non-exempt amounts
def relocation_split(moving, temporary, moving_ok=False, temporary_ok=False):
    relief = relocation_relief(moving, temporary, moving_ok, temporary_ok)

    moving_cost = Decimal(str(moving))
    temporary_cost = Decimal(str(temporary))

    remaining = relief["exempt"]

    moving_exempt = min(moving_cost, remaining) if moving_ok else Decimal("0")
    remaining -= moving_exempt

    temporary_exempt = min(temporary_cost, remaining) if temporary_ok else Decimal("0")

    qualifying_excess = relief["qualifying"] - relief["exempt"]
    non_qualifying = relief["total"] - relief["qualifying"]

    return {
        "moving_exempt": moving_exempt,
        "temporary_exempt": temporary_exempt,
        "moving_non_exempt": moving_cost - moving_exempt,
        "temporary_non_exempt": temporary_cost - temporary_exempt,
        "qualifying_excess": qualifying_excess,
        "non_qualifying": non_qualifying,
        "total_exempt": relief["exempt"],
        "total_non_exempt": relief["non_exempt"]
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

# Group taxable cash and benefits in kind
def benefit_values(cash, kind):
    try:
        cash_value = Decimal(str(cash))
        kind_value = Decimal(str(kind))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid taxable benefit amount.")

    if any(
        not value.is_finite() or value < 0
        for value in (cash_value, kind_value)
    ):
        raise ValueError("Taxable benefits must be finite and non-negative.")

    return {
        "taxable_cash": cash_value,
        "taxable_kind": kind_value,
        "total_taxable": cash_value + kind_value
    }

# Classify taxable relocation expenses by payment method
def relocation_tax(relief, payment):
    methods = ("employer_direct", "employee_direct", "reimbursed")

    if payment not in methods:
        raise ValueError("Invalid relocation payment method.")

    excess = relief["qualifying_excess"]
    non_qualifying = relief["non_qualifying"]

    if payment == "reimbursed":
        taxable_cash = non_qualifying
        taxable_kind = excess
    else:
        taxable_cash = Decimal("0")
        taxable_kind = excess + non_qualifying
    
    paye = non_qualifying if payment == "reimbursed" else Decimal("0")

    p11d = excess if payment == "reimbursed" else excess + non_qualifying

    class1 = non_qualifying if payment != "employer_direct" else Decimal("0")

    class1a = excess + (
        non_qualifying if payment == "employer_direct" else Decimal("0")
    )

    return {
        "taxable_cash": taxable_cash,
        "taxable_kind": taxable_kind,
        "total_taxable": taxable_cash + taxable_kind,
        "payment_method": payment,
        "paye_value": paye,
        "p11d_value": p11d,
        "uk_class1_base": class1,
        "uk_class1a_base": class1a
    }
