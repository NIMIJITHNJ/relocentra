from decimal import Decimal, InvalidOperation

AHV_RATE = Decimal("0.053")
ALV_RATE = Decimal("0.011")
ALV_LIMIT = Decimal("148200")

# Calculate Swiss employee social security contributions
def employee_social(income):
    try:
        salary = Decimal(str(income))
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError("Invalid annual income.")

    if not salary.is_finite() or salary < 0:
        raise ValueError("Income must be finite and non-negative.")

    ahv = salary * AHV_RATE
    alv = min(salary, ALV_LIMIT) * ALV_RATE

    return {
        "ahv": ahv,
        "alv": alv,
        "total": ahv + alv
    }

# Calculate basic Swiss employer social security contributions
def employer_social(income):
    contributions = employee_social(income)

    return {
        "ahv": contributions["ahv"],
        "alv": contributions["alv"],
        "total": contributions["total"]
    }

# Identify Swiss social security coverage based on certificate confirmation
def coverage_status(certificate):
    if not isinstance(certificate, bool):
        raise ValueError("Certificate status must be True or False.")

    if certificate:
        return {
            "country": "Switzerland",
            "uk_ni": False,
            "status": "Swiss coverage confirmed"
        }

    return {
        "country": None,
        "uk_ni": None,
        "status": "Coverage requires verification"
    }

# Calculate standard UK employer Class 1 National Insurance
def uk_employer_ni(earnings, threshold):
    earnings = Decimal(str(earnings))
    threshold = Decimal(str(threshold))

    if not earnings.is_finite() or not threshold.is_finite():
        raise ValueError("Earnings and threshold must be finite.")

    if earnings < 0 or threshold < 0:
        raise ValueError("Earnings and threshold cannot be negative.")

    taxable = max(earnings - threshold, Decimal("0"))

    return taxable * Decimal("0.15")

# Calculate standard UK employee Class 1 National Insurance
def uk_employee_ni(earnings):
    try:
        income = Decimal(str(earnings))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid UK employee earnings.")

    if not income.is_finite() or income < 0:
        raise ValueError("Employee earnings must be finite and non-negative.")

    primary = Decimal("12570")
    upper = Decimal("50270")

    main_band = max(min(income, upper) - primary, Decimal("0"))
    higher_band = max(income - upper, Decimal("0"))

    main_ni = main_band * Decimal("0.08")
    higher_ni = higher_band * Decimal("0.02")

    return {
        "main": main_ni,
        "higher": higher_ni,
        "total": main_ni + higher_ni
    }

# Calculate UK employer Class 1A National Insurance on applicable benefits
def uk_class1a_ni(benefits):
    benefits = Decimal(str(benefits))

    if not benefits.is_finite():
        raise ValueError("Benefits must be finite.")

    if benefits < 0:
        raise ValueError("Benefits cannot be negative.")

    return benefits * Decimal("0.15")

# Calculate combined UK employer National Insurance charges
def uk_ni_charges(earnings, benefits, threshold):
    class1 = uk_employer_ni(earnings, threshold)
    class1a = uk_class1a_ni(benefits)

    return {
        "class1": class1,
        "class1a": class1a,
        "total": class1 + class1a
    }

# Determine UK National Insurance based on confirmed coverage
def ni_scenario(earnings, benefits, threshold, certificate=False):
    coverage = coverage_status(certificate)

    if coverage["uk_ni"] is False:
        return {
            "applicable": False,
            "liability": Decimal("0"),
            "illustrative": None,
            "status": "UK NI exempt under confirmed Swiss coverage"
        }

    return {
        "applicable": None,
        "liability": None,
        "illustrative": uk_ni_charges(earnings, benefits, threshold),
        "status": "UK NI liability requires verification"
    }
