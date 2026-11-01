from decimal import Decimal, InvalidOperation
from .uk_tax import uk_incometax


# Calculate employer paid UK tax using iterative gross-up
def tax_grossup(taxable_income):
    try:
        income = Decimal(str(taxable_income))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid taxable income.")

    if not income.is_finite() or income < 0:
        raise ValueError("Taxable income must be a finite, non-negative number.")

    tax = Decimal("0")
    tolerance = Decimal("0.000001")
    max_iter = 100

    for _ in range(max_iter):
        new_tax = uk_incometax(income + tax)

        if abs(new_tax - tax) < tolerance:
            return new_tax

        tax = new_tax

    raise ValueError("Tax gross-up calculation did not converge.")
