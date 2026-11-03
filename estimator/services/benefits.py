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

# Calculate the basic value of employer-rented accommodation
def housing_value(annual_rent, annual_value, employee_rent=0):
    try:
        rent = Decimal(str(annual_rent))
        value = Decimal(str(annual_value))
        contribution = Decimal(str(employee_rent))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid accommodation value.")

    amounts = (rent, value, contribution)

    if any(not amount.is_finite() or amount < 0 for amount in amounts):
        raise ValueError("Accommodation amounts must be finite and non-negative.")

    basic_value = max(
        Decimal("0"),
        max(rent, value) - contribution
    )

    return {
        "annual_rent": rent,
        "annual_value": value,
        "employee_rent": contribution,
        "basic_value": basic_value
    }

# Calculate accommodation value including the additional property cost charge
def housing_extra(annual_rent, annual_value, property_cost, interest_rate,
                  employee_rent=0):

    basic = housing_value(annual_rent, annual_value, employee_rent)

    try:
        cost = Decimal(str(property_cost))
        rate = Decimal(str(interest_rate))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid accommodation cost or interest rate.")

    if not cost.is_finite() or not rate.is_finite():
        raise ValueError("Accommodation values must be finite.")

    if cost < 0 or rate < 0 or rate > 1:
        raise ValueError("Invalid property cost or interest rate.")

    excess_cost = max(cost - Decimal("75000"), Decimal("0"))

    unused_rent = max(
        basic["employee_rent"]
        - max(basic["annual_rent"], basic["annual_value"]),
        Decimal("0")
    )

    additional = max(
        excess_cost * rate - unused_rent,
        Decimal("0")
    )

    return {
        "basic_value": basic["basic_value"],
        "additional_value": additional,
        "taxable_value": basic["basic_value"] + additional
    }

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

# Calculate accommodation expenditure, benefit value and taxable amount
def housing_assessment(monthly_rent, annual_value, property_cost,
                       interest_rate, employee_rent=0, relief=0,
                       employer_recovery=0, relief_verified=False,
                       assignment=None):

    expenditure = housing_cost(monthly_rent)
    
    try:
        recovery = Decimal(str(employer_recovery))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid employer recovery amount.")

    if not recovery.is_finite() or recovery < 0:
        raise ValueError("Employer recovery must be finite and non-negative.")

    if recovery > expenditure:
        raise ValueError("Employer recovery cannot exceed housing expenditure.")

    net_cost = expenditure - recovery


    valuation = housing_extra(
        expenditure,
        annual_value,
        property_cost,
        interest_rate,
        employee_rent
    )
        
    if not isinstance(relief_verified, bool):
        raise ValueError("Relief verification must be True or False.")

    try:
        relief_amount = Decimal(str(relief))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid accommodation relief.")

    eligibility = "not_assessed"

    if relief_amount > 0 and assignment is None:
        raise ValueError(
            "Assignment details are required to assess accommodation relief."
        )

    if assignment is not None:
        if not isinstance(assignment, dict):
            raise ValueError("Invalid assignment details.")

        employment = assignment.get("employment")
        purpose = assignment.get("temporary_purpose")
        months = assignment.get("expected_months")
        additional = assignment.get("additional_cost")
        reasonable = assignment.get("reasonable_cost")

        try:
            work = Decimal(str(assignment.get("work_percent", 100)))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Invalid working time percentage.")

        if employment not in ("continuing", "new", "unknown"):
            raise ValueError("Invalid employment arrangement.")

        if any(
            value is not None and not isinstance(value, bool)
            for value in (purpose, additional, reasonable)
        ):
            raise ValueError("Invalid assignment condition.")

        if months is not None and (
            isinstance(months, bool)
            or not isinstance(months, int)
            or months <= 0
        ):
            raise ValueError("Invalid assignment duration.")

        if not work.is_finite() or work < 0 or work > 100:
            raise ValueError("Working time must be between 0 and 100.")

        if (
            purpose is False
            or additional is False
            or (months is not None and months > 24 and work >= 40)
        ):
            eligibility = "not_qualifying"

        elif (
            employment == "continuing"
            and purpose is True
            and months is not None
            and months <= 24
            and additional is True
            and reasonable is True
        ):
            eligibility = "potentially_qualifying"

        else:
            eligibility = "requires_review"

        if relief_amount > 0 and eligibility != "potentially_qualifying":
            raise ValueError(
                "Accommodation relief is not supported by the assignment conditions."
            )

    if relief_amount > 0 and not relief_verified:
        raise ValueError(
            "Accommodation tax relief requires verified eligibility."
        )

    tax = housing_tax(
        valuation["taxable_value"],
        relief
    )

    return {
        "employer_cost": expenditure,
        "employer_recovery": recovery,
        "employer_net_cost": net_cost,
        "basic_value": valuation["basic_value"],
        "additional_value": valuation["additional_value"],
        "relief_verified": relief_verified,
        "eligibility": eligibility,
        "gross_benefit": tax["gross"],
        "relief": tax["relief"],
        "taxable_benefit": tax["taxable"]
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
