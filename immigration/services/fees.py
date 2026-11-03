from decimal import Decimal, InvalidOperation, ROUND_CEILING


VISA_OUT = (Decimal("819"), Decimal("1618"))
VISA_IN = (Decimal("943"), Decimal("1865"))

IHS_YEAR = Decimal("1035")
COS_FEE = Decimal("525")
ETA_FEE = Decimal("20")
PRIORITY_FEE = Decimal("500")
SUPER_FEE = Decimal("1000")
LICENCE_PRIORITY_FEE = Decimal("750")
COS_PRIORITY_FEE = Decimal("350")
MAINTENANCE = Decimal("1270")

ISC_RATES = {
    "small": (Decimal("480"), Decimal("240")),
    "large": (Decimal("1320"), Decimal("660")),
}

LICENCE_RATES = {
    "small": Decimal("611"),
    "large": Decimal("1682"),
}

UPGRADE_RATES = {
    "small": Decimal("0"),
    "large": Decimal("1071"),
}


# Validate numeric inputs
def check_num(value, name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Invalid {name}.")

    if not number.is_finite() or number <= 0:
        raise ValueError(f"{name} must be positive.")

    return number


# Calculate immigration costs
def visa_fees(
    assignment_months,
    permission_months,
    sponsor_size="large",
    location="outside",
    licence_status="existing",
    isc_exempt=False,
    priority="none",
    eta=False,
    employer_pays_visa=False,
    employer_pays_ihs=False,
    employer_pays_priority=False,
    employer_pays_eta=False,
    maintenance_certified=False,
    licence_priority=False,
    cos_priority=False,
    extra_cos_needed=False,
):
    months = check_num(assignment_months, "assignment duration")
    permission = check_num(permission_months, "visa duration")

    if months != months.to_integral_value() or months > 60:
        raise ValueError("Assignment duration must be 1 to 60 whole months.")
    
    if permission < months:
        raise ValueError("Visa duration cannot be shorter than the assignment.")

    if sponsor_size not in ISC_RATES:
        raise ValueError("Invalid sponsor size.")

    if location not in ("inside", "outside"):
        raise ValueError("Invalid application location.")

    if licence_status not in ("existing", "new", "add_worker"):
        raise ValueError("Invalid sponsor licence status.")

    if priority not in ("none", "priority", "super"):
        raise ValueError("Invalid priority option.")

    if licence_priority and licence_status != "new":
        raise ValueError("Licence priority requires a new licence.")

    if cos_priority and not extra_cos_needed:
        raise ValueError("CoS priority requires an additional allocation.")

    flags = (
        isc_exempt, eta, employer_pays_visa,
        employer_pays_ihs, employer_pays_priority,
        employer_pays_eta, maintenance_certified,
        licence_priority, cos_priority, extra_cos_needed
    )

    if any(type(value) is not bool for value in flags):
        raise ValueError("Invalid boolean option.")

    # Select application fee from the visa duration
    visa_rates = VISA_OUT if location == "outside" else VISA_IN
    visa = visa_rates[0] if permission <= 36 else visa_rates[1]

    # Charge IHS in six-month blocks
    blocks = (permission / Decimal("6")).to_integral_value(
        rounding=ROUND_CEILING
    )

    if location == "outside" and permission <= 6:
        ihs = Decimal("0")
    else:
        ihs = blocks * IHS_YEAR / Decimal("2")

    # Calculate the sponsor's Immigration Skills Charge
    isc = Decimal("0")

    chargeable = (
        not isc_exempt
        and (location == "inside" or months >= 6)
    )

    if chargeable:
        first, extra = ISC_RATES[sponsor_size]

        extra_blocks = max(
            0,
            (int(months) - 12 + 5) // 6
        )

        isc = first + extra_blocks * extra

    # Include licence fees only when applicable
    licence = Decimal("0")

    if licence_status == "new":
        licence = LICENCE_RATES[sponsor_size]
    elif licence_status == "add_worker":
        licence = UPGRADE_RATES[sponsor_size]

    # Calculate optional fees
    priority_cost = {
        "none": Decimal("0"),
        "priority": PRIORITY_FEE,
        "super": SUPER_FEE,
    }[priority]

    eta_cost = ETA_FEE if eta else Decimal("0")
    licence_fast = LICENCE_PRIORITY_FEE if licence_priority else Decimal("0")
    cos_fast = COS_PRIORITY_FEE if cos_priority else Decimal("0")
    mandatory = COS_FEE + isc + licence
    sponsor_optional = licence_fast + cos_fast
    applicant = visa + ihs
    optional = priority_cost + eta_cost + sponsor_optional

    overall = mandatory + applicant + optional

    # Calculate costs voluntarily funded by the employer
    employer_extra = Decimal("0")

    if employer_pays_visa:
        employer_extra += visa

    if employer_pays_ihs:
        employer_extra += ihs

    if employer_pays_priority:
        employer_extra += priority_cost

    if employer_pays_eta:
        employer_extra += eta_cost

    employer_total = mandatory + sponsor_optional + employer_extra
    employee_total = overall - employer_total

    proof_funds = (
        Decimal("0") if maintenance_certified
        else MAINTENANCE
    )

    return {
        "visa": visa,
        "ihs": ihs,
        "cos": COS_FEE,
        "isc": isc,
        "licence": licence,
        "priority": priority_cost,
        "eta": eta_cost,
        "licence_priority": licence_fast,
        "cos_priority": cos_fast,
        "mandatory_employer": mandatory,
        "applicant_fees": applicant,
        "optional_fees": optional,
        "overall_total": overall,
        "employer_total": employer_total,
        "employee_total": employee_total,
        "maintenance_evidence": proof_funds,
        "ihs_blocks": blocks if ihs else Decimal("0"),
    }
