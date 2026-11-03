from decimal import Decimal, InvalidOperation


MIN_SALARY = Decimal("52500")
HIGH_EARNER = Decimal("73900")
MAX_HOURS = Decimal("48")
STANDARD_HOURS = Decimal("37.5")


# Validate financial and numerical inputs
def check_number(value, name, positive=False):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid {name}.")

    if not number.is_finite():
        raise ValueError(f"Invalid {name}.")

    if positive and number <= 0:
        raise ValueError(f"{name} must be positive.")

    if not positive and number < 0:
        raise ValueError(f"{name} cannot be negative.")

    return number


# Validate confirmed, rejected or unknown conditions
def check_flag(value, name):
    if value is not None and type(value) is not bool:
        raise ValueError(f"Invalid {name}.")
    return value


# Assess Senior or Specialist Worker requirements
def visa_checks(
    salary_chf,
    rate,
    overseas_months,
    weekly_hours=37.5,
    going_rate_gbp=None,
    going_rate_hours=37.5,
    occupation_code=None,
    occupation_eligible=None,
    sponsor_licensed=None,
    sponsor_a_rated=None,
    cos_valid=None,
    corporate_link=None,
    current_employee=None,
    genuine_job=None,
    isc_compliant=None,
    allowed_allowance_chf=0,
    housing_allowance_chf=0
):
    salary = check_number(salary_chf, "salary")
    exchange_rate = check_number(rate, "exchange rate", True)
    months = check_number(overseas_months, "employment months")
    hours = check_number(weekly_hours, "weekly hours", True)
    reference_hours = check_number(
        going_rate_hours, "going rate reference hours", True
    )

    allowed = check_number(
        allowed_allowance_chf, "permitted allowances"
    )
    housing = check_number(
        housing_allowance_chf, "housing allowance"
    )

    if months != months.to_integral_value():
        raise ValueError("Employment months must be a whole number.")

    if occupation_code is not None:
        occupation_code = str(occupation_code)

        if len(occupation_code) != 4 or not occupation_code.isascii() or not occupation_code.isdigit():
            raise ValueError("Occupation code must contain four digits.")

    conditions = {
        "occupation": check_flag(
            occupation_eligible, "occupation eligibility"
        ),
        "sponsor": check_flag(
            sponsor_licensed, "sponsor licence"
        ),
        "sponsor_rating": check_flag(
            sponsor_a_rated, "sponsor rating"
        ),
        "certificate": check_flag(
            cos_valid, "certificate of sponsorship"
        ),
        "corporate_link": check_flag(
            corporate_link, "corporate relationship"
        ),
        "current_employee": check_flag(
            current_employee, "current employment"
        ),
        "genuine_job": check_flag(
            genuine_job, "genuine vacancy"
        ),
        "skills_charge": check_flag(
            isc_compliant, "Immigration Skills Charge"
        ),
    }

    base_pay = salary + allowed

    # Limit qualifying accommodation allowances to 30% of the package
    housing_limit = base_pay / Decimal("0.70") - base_pay
    eligible_housing = min(housing, housing_limit)

    salary_gbp = salary / exchange_rate
    eligible_salary = (
        base_pay + eligible_housing
    ) / exchange_rate

    # Count no more than 48 hours for the general salary threshold
    general_salary = eligible_salary * (
        min(hours, MAX_HOURS) / hours
    )

    salary_met = general_salary >= MIN_SALARY
    high_earner = general_salary >= HIGH_EARNER
    employment_met = months >= 12 or high_earner

    going_rate = None
    adjusted_rate = None
    going_rate_met = None

    if going_rate_gbp is not None:
        going_rate = check_number(
            going_rate_gbp, "occupation going rate", True
        )
        adjusted_rate = (
            going_rate * hours / reference_hours
        )
        going_rate_met = eligible_salary >= adjusted_rate

    # An occupation cannot be verified without its code
    if occupation_code is None:
        conditions["occupation"] = None

    conditions["salary"] = salary_met
    conditions["employment"] = employment_met
    conditions["going_rate"] = going_rate_met

    failed = [
        name for name, met in conditions.items()
        if met is False
    ]

    pending = [
        name for name, met in conditions.items()
        if met is None
    ]

    if failed:
        status = "requirements_not_met"
    elif pending:
        status = "verification_required"
    else:
        status = "core_requirements_met"

    return {
        "salary_gbp": salary_gbp,
        "eligible_salary": eligible_salary,
        "general_salary": general_salary,
        "salary_met": salary_met,
        "high_earner": high_earner,
        "employment_met": employment_met,
        "occupation_code": occupation_code,
        "going_rate": going_rate,
        "adjusted_rate": adjusted_rate,
        "going_rate_met": going_rate_met,
        "housing_allowance_used": eligible_housing / exchange_rate,
        "conditions": conditions,
        "failed": failed,
        "pending": pending,
        "status": status,
    }
