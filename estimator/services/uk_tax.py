
from decimal import Decimal

# UK Income Tax configuration for 2026/27
PERSONAL_ALLOWANCE = Decimal("12570")
PERSONAL_ALLOWANCE_TAPER_START = Decimal("100000")

BASIC_RATE_BAND = Decimal("37700")
ADDITIONAL_RATE_THRESHOLD = Decimal("125140")

BASIC_RATE = Decimal("0.20")
HIGHER_RATE = Decimal("0.40")
ADDITIONAL_RATE = Decimal("0.45")


# Calculate UK personal allowance based on adjusted net income
def personal_allowance(adjusted_net_income):
    income = Decimal(str(adjusted_net_income))

    if not income.is_finite() or income < 0:
        raise ValueError("Income must be a finite, non-negative number.")

    if income <= PERSONAL_ALLOWANCE_TAPER_START:
        return PERSONAL_ALLOWANCE

    reduction = (income - PERSONAL_ALLOWANCE_TAPER_START) / Decimal("2")
    remaining_allowance = PERSONAL_ALLOWANCE - reduction

    return max(Decimal("0"), remaining_allowance)


# Calculate UK income tax using the 2026/27 England tax bands
def uk_incometax(annual_income):
    income = Decimal(str(annual_income))

    if not income.is_finite() or income < 0:
        raise ValueError("Income must be a finite, non-negative number.")

    allowance = personal_allowance(income)
    taxable_income = max(Decimal("0"), income - allowance)

    basic_band = min(taxable_income, BASIC_RATE_BAND)
    higher_band = max(
        Decimal("0"),
        min(taxable_income, ADDITIONAL_RATE_THRESHOLD) - BASIC_RATE_BAND
    )
    additional_band = max(
        Decimal("0"),
        taxable_income - ADDITIONAL_RATE_THRESHOLD
    )

    total_tax = (
        basic_band * BASIC_RATE
        + higher_band * HIGHER_RATE
        + additional_band * ADDITIONAL_RATE
    )

    return total_tax
