from decimal import Decimal, InvalidOperation

from .fees import ETA_FEE


ETA_SOURCE = "https://www.gov.uk/eta"
EXEMPT_SOURCE = "https://www.gov.uk/eta/when-not-need-eta"
APPLY_SOURCE = "https://www.gov.uk/eta/apply"
BUSINESS_SOURCE = "https://www.gov.uk/standard-visitor/visit-on-business"
VISITOR_SOURCE = "https://www.gov.uk/standard-visitor"
SWISS_SOURCE = "https://www.gov.uk/guidance/visiting-the-uk-as-an-eu-eea-or-swiss-citizen"

PERMITTED = {
    "meetings",
    "conferences",
    "negotiations",
    "site_visit",
}

REVIEW = {
    "training",
    "other",
}

EXEMPTIONS = {
    "none",
    "uk_permission",
    "british_irish",
    "ireland_resident_cta",
}


# Validate the planned visit duration
def check_months(value):
    try:
        months = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid business visit duration.")

    if not months.is_finite() or months <= 0:
        raise ValueError("Business visit duration must be positive.")

    return months


# Assess a Swiss national's pre-assignment business visit
def visitor_checks(
    purpose="meetings",
    visit_months=1,
    passport_valid=True,
    eta_exemption="none",
    has_valid_eta=False
):
    months = check_months(visit_months)

    if purpose not in PERMITTED | REVIEW | {"uk_employment"}:
        raise ValueError("Invalid business visit purpose.")

    if eta_exemption not in EXEMPTIONS:
        raise ValueError("Invalid ETA exemption.")

    if type(passport_valid) is not bool:
        raise ValueError("Invalid passport status.")

    if type(has_valid_eta) is not bool:
        raise ValueError("Invalid ETA status.")

    warnings = []

    if not passport_valid:
        status = "passport_invalid"

    elif months > 6:
        status = "visit_too_long"

    elif purpose == "uk_employment":
        status = "work_visa_required"

    elif purpose in REVIEW:
        status = "activity_verification_required"

    else:
        status = "visitor_activity_permitted"

    visitor_possible = status == "visitor_activity_permitted"

    if status == "work_visa_required":
        visa_status = "work_visa_required"

    elif status in ("passport_invalid", "visit_too_long"):
        visa_status = "requirements_not_met"

    elif status == "activity_verification_required":
        visa_status = "verification_required"

    else:
        visa_status = "visitor_visa_not_required"

    # Assess ETA only when the visitor activity is suitable
    eta_required = None
    eta_application_needed = None

    if visitor_possible:
        eta_required = eta_exemption == "none"
        eta_application_needed = (
            eta_required and not has_valid_eta
        )

    eta_cost = (
        ETA_FEE if eta_application_needed
        else Decimal("0")
    )

    if eta_exemption == "british_irish":
        warnings.append(
            "British or Irish citizenship requires appropriate "
            "evidence of that citizenship for travel."
        )

    if eta_exemption == "ireland_resident_cta":
        warnings.append(
            "The exemption applies only when the person lives "
            "in Ireland and enters from Ireland, Guernsey, "
            "Jersey or the Isle of Man. Supporting evidence "
            "may be required."
        )

    if purpose == "training":
        warnings.append(
            "Work-related training may be permitted, but its "
            "specific conditions must be verified."
        )

    if purpose == "other":
        warnings.append(
            "The planned activity must be checked against "
            "the official permitted activities."
        )

    if status == "work_visa_required":
        warnings.append(
            "Ordinary employment with the UK subsidiary "
            "cannot be undertaken using visitor permission."
        )

    if status == "visit_too_long":
        warnings.append(
            "A Standard Visitor normally cannot stay "
            "for longer than six months."
        )

    if status == "passport_invalid":
        warnings.append(
            "A valid passport or accepted travel document "
            "is required for the visit."
        )

    warnings.append(
        "An ETA does not guarantee entry and does not "
        "replace the work visa for the two-year assignment."
    )

    return {
        "nationality": "Swiss",
        "purpose": purpose,
        "visit_months": months,
        "passport_valid": passport_valid,
        "status": status,
        "visa_status": visa_status,
        "eta_required": eta_required,
        "eta_application_needed": eta_application_needed,
        "eta_cost": eta_cost,
        "eta_exemption": eta_exemption,
        "max_visit_months": Decimal("6"),
        "eta_validity_months": Decimal("24"),
        "eta_processing": (
            "Usually within one day; allow up to "
            "three working days."
        ),
        "permitted_activities": sorted(PERMITTED),
        "warnings": warnings,
        "sources": {
            "swiss_visitors": SWISS_SOURCE,
            "business_activities": BUSINESS_SOURCE,
            "visitor_rules": VISITOR_SOURCE,
            "eta": ETA_SOURCE,
            "eta_exemptions": EXEMPT_SOURCE,
            "eta_application": APPLY_SOURCE,
        },
    }
