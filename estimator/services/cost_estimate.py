from decimal import Decimal, InvalidOperation
from .currency import convert_currency
from .benefits import housing_cost, relocation_cash, relocation_relief, benefit_values, relocation_split, relocation_tax
from .gross_up import tax_grossup
from .social_security import employer_social, employee_social

# Calculate annual employer cost from individual financial components
def year_cost(home_pay, benefits, host_tax, employer_charges, hypo_tax, hypo_social):
    try:
        values = [
            Decimal(str(value))
            for value in (
                home_pay, benefits, host_tax,
                employer_charges, hypo_tax, hypo_social
            )
        ]
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid employer cost input.")

    if any(not value.is_finite() or value < 0 for value in values):
        raise ValueError("Cost components must be finite and non-negative.")

    pay, benefits, tax, charges, swiss_tax, swiss_social = values

    total = pay + benefits + tax + charges - swiss_tax - swiss_social

    return {
        "home_pay": pay,
        "benefits": benefits,
        "host_tax": tax,
        "employer_charges": charges,
        "hypo_tax": swiss_tax,
        "hypo_social": swiss_social,
        "total": total
    }

# Calculate total assignment cost and its multiple of home pay
def assignment_total(year1, year2):
    try:
        cost1 = Decimal(str(year1["total"]))
        cost2 = Decimal(str(year2["total"]))
        pay1 = Decimal(str(year1["home_pay"]))
        pay2 = Decimal(str(year2["home_pay"]))
    except (KeyError, TypeError, ValueError, InvalidOperation):
        raise ValueError("Invalid annual cost data.")

    if any(
        not value.is_finite() or value < 0
        for value in (cost1, cost2, pay1, pay2)
    ):
        raise ValueError("Annual costs and home pay must be non-negative.")

    total_cost = cost1 + cost2
    total_pay = pay1 + pay2

    multiple = total_cost / total_pay if total_pay > 0 else None

    return {
        "year1": cost1,
        "year2": cost2,
        "total": total_cost,
        "home_pay": total_pay,
        "multiple": multiple
    }

# Calculate annual home salary and bonus in GBP
def home_pay(salary, bonus, currency, exchange_rate):
    try:
        salary = Decimal(str(salary))
        bonus = Decimal(str(bonus))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid salary or bonus.")

    if any(not value.is_finite() or value < 0 for value in (salary, bonus)):
        raise ValueError("Salary and bonus must be finite and non-negative.")

    salary_gbp = convert_currency(salary, currency, "GBP", exchange_rate)
    bonus_gbp = convert_currency(bonus, currency, "GBP", exchange_rate)

    return {
        "salary": salary_gbp,
        "bonus": bonus_gbp,
        "total": salary_gbp + bonus_gbp
    }

# Convert hypothetical Swiss tax and social security deductions into GBP
def hypo_deductions(tax_chf, social_chf, exchange_rate):
    try:
        tax = Decimal(str(tax_chf))
        social = Decimal(str(social_chf))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid Swiss deduction amount.")

    if any(not value.is_finite() or value < 0 for value in (tax, social)):
        raise ValueError("Swiss deductions must be finite and non-negative.")

    tax_gbp = convert_currency(tax, "CHF", "GBP", exchange_rate)
    social_gbp = convert_currency(social, "CHF", "GBP", exchange_rate)

    return {
        "hypo_tax": tax_gbp,
        "hypo_social": social_gbp,
        "total": tax_gbp + social_gbp
    }

# Calculate annual assignment benefits and employer expenditure
def year_benefits(year, monthly_rent, relocation, moving, temporary, rate):
    if year not in (1, 2) or isinstance(year, bool):
        raise ValueError("Assignment year must be 1 or 2.")

    housing = housing_cost(monthly_rent)

    expenses = relocation_relief(moving, temporary)
    cash = relocation_cash(relocation, "CHF", rate)

    if year == 1:
        relocation_cost = cash["cost"]
        moving_cost = Decimal(str(moving))
        temporary_cost = Decimal(str(temporary))
    else:
        relocation_cost = Decimal("0")
        moving_cost = Decimal("0")
        temporary_cost = Decimal("0")

    total = housing + relocation_cost + (expenses["total"] if year == 1 else Decimal("0"))

    return {
        "housing": housing,
        "relocation": relocation_cost,
        "moving": moving_cost,
        "temporary": temporary_cost,
        "total": total
    }

# Calculate starting taxable income for UK tax gross-up
def grossup_base(home, deductions, taxable):
    try:
        pay = Decimal(str(home))
        hypo = Decimal(str(deductions))
        benefits = Decimal(str(taxable))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid gross-up input.")

    values = (pay, hypo, benefits)

    if any(not value.is_finite() or value < 0 for value in values):
        raise ValueError("Gross-up inputs must be finite and non-negative.")

    if hypo > pay:
        raise ValueError("Hypothetical deductions cannot exceed home pay.")

    return pay - hypo + benefits

# Calculate employer paid UK tax using the gross-up method
def host_tax(home, deductions, taxable):
    base = grossup_base(home, deductions, taxable)
    tax = tax_grossup(base)

    return {
        "taxable_base": base,
        "employer_tax": tax
    }

# Convert basic Swiss employer social security charges into GBP
def swiss_charges(income_chf, exchange_rate):
    contributions = employer_social(income_chf)

    ahv = convert_currency(
        contributions["ahv"], "CHF", "GBP", exchange_rate
    )

    alv = convert_currency(
        contributions["alv"], "CHF", "GBP", exchange_rate
    )

    return {
        "ahv": ahv,
        "alv": alv,
        "total": ahv + alv
    }

# Estimate annual employer cost using the existing calculation modules
def estimate_year(year, salary, bonus, rate, swiss_tax,
                  monthly_rent, relocation, moving, temporary, taxable_kind,
                  moving_ok=False, temporary_ok=False,
                  payment="employer_direct"):

    pay = home_pay(salary, bonus, "CHF", rate)

    income_chf = Decimal(str(salary)) + Decimal(str(bonus))
    social = employee_social(income_chf)

    deductions = hypo_deductions(swiss_tax, social["total"], rate)

    benefits = year_benefits(
        year, monthly_rent, relocation, moving, temporary, rate
    )

    relief = relocation_split(
        benefits["moving"],
        benefits["temporary"],
        moving_ok,
        temporary_ok
    )

    reporting = relocation_tax(relief, payment)
    
    cash_total = benefits["relocation"] + reporting["taxable_cash"]
    kind_total = Decimal(str(taxable_kind)) + reporting["taxable_kind"]

    taxable = benefit_values(cash_total, kind_total)


    tax = host_tax(
        pay["total"], deductions["total"], taxable["total_taxable"]
    )

    charges = swiss_charges(income_chf, rate)

    cost = year_cost(
        pay["total"],
        benefits["total"],
        tax["employer_tax"],
        charges["total"],
        deductions["hypo_tax"],
        deductions["hypo_social"]
    )

    return {
        "pay": pay,
        "benefits": benefits,
        "deductions": deductions,        
        "relief": relief,
        "reporting": reporting,
        "taxable": taxable,
        "tax": tax,
        "charges": charges,
        "cost": cost
    }

# Calculate the complete two-year assignment cost
def estimate_assignment(salary, bonus, rate, swiss_tax, monthly_rent,
                        relocation, moving, temporary, taxable_kind1, taxable_kind2,
                        moving_ok=False, temporary_ok=False,
                        payment="employer_direct"):

    year1 = estimate_year(
        1, salary, bonus, rate, swiss_tax,
        monthly_rent, relocation, moving, temporary, taxable_kind1,
        moving_ok, temporary_ok, payment
    )

    year2 = estimate_year(
        2, salary, bonus, rate, swiss_tax,
        monthly_rent, relocation, moving, temporary, taxable_kind2,
        moving_ok, temporary_ok, payment
    )

    summary = assignment_total(year1["cost"], year2["cost"])

    return {
        "year1": year1,
        "year2": year2,
        "summary": summary
    }
