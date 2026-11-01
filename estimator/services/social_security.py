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
