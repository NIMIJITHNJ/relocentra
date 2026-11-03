from decimal import Decimal, InvalidOperation


DOC_SOURCE = "https://www.gov.uk/senior-specialist-worker-visa/documents-you-need-to-apply"
FINANCE_SOURCE = "https://www.gov.uk/senior-specialist-worker-visa/how-much-it-costs"
TB_SOURCE = "https://www.gov.uk/tb-test-visa/tb-test-visa"
RULES_SOURCE = "https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-global-business-mobility-routes"

HIGH_EARNER = Decimal("73900")
MAINTENANCE = Decimal("1270")


# Validate numerical document assessment inputs
def check_number(value, name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid {name}.")

    if not number.is_finite() or number < 0:
        raise ValueError(f"Invalid {name}.")

    return number


# Build the visa document requirements checklist
def document_checks(
    eligible_salary_gbp,
    uk_months=0,
    sponsor_maintenance=False,
    tb_required=None,
    atas_required=None,
    dependants=False,
    translations_required=None,
    scholarship_consent=None
):
    salary = check_number(eligible_salary_gbp, "eligible salary")
    residence = check_number(uk_months, "UK residence")

    if residence != residence.to_integral_value():
        raise ValueError("UK residence must be in whole months.")

    flags = (
        sponsor_maintenance,
        tb_required,
        atas_required,
        dependants,
        translations_required,
        scholarship_consent,
    )

    if any(value is not None and type(value) is not bool for value in flags):
        raise ValueError("Invalid document assessment option.")

    if sponsor_maintenance is None or dependants is None:
        raise ValueError("Required assessment options cannot be unknown.")

    items = []

    def add(code, title, status, details, source):
        items.append({
            "code": code,
            "title": title,
            "status": status,
            "details": details,
            "source": source,
        })

    add(
        "passport",
        "Valid passport or acceptable travel document",
        "required",
        "Must establish the applicant's identity and nationality.",
        DOC_SOURCE
    )

    add(
        "cos",
        "Certificate of Sponsorship reference",
        "required",
        "The CoS must be valid and assigned no more than three months before applying.",
        RULES_SOURCE
    )

    add(
        "employment",
        "Job title, annual salary and occupation code",
        "required",
        "The applicant needs the sponsored employment details.",
        DOC_SOURCE
    )

    add(
        "sponsor",
        "Employer name and sponsor licence number",
        "required",
        "These details are normally recorded on the CoS.",
        DOC_SOURCE
    )

    funds_required = residence < 12 and not sponsor_maintenance

    add(
        "funds",
        "Financial maintenance evidence",
        "required" if funds_required else "not_required",
        "If required, show at least £1,270 held for 28 consecutive days, with the period ending within 31 days of applying.",
        FINANCE_SOURCE
    )

    add(
        "overseas",
        "Evidence of overseas employment",
        "may_be_requested" if salary < HIGH_EARNER else "not_required",
        "Applicants below the high-earner threshold may be asked for payslips or other evidence of at least 12 months of overseas employment.",
        DOC_SOURCE
    )

    add(
        "tb",
        "Tuberculosis test certificate",
        "verify" if tb_required is None else (
            "required" if tb_required else "not_required"
        ),
        "Depends on residence history in a listed country, not Swiss nationality alone.",
        TB_SOURCE
    )

    add(
        "atas",
        "Academic Technology Approval Scheme certificate",
        "verify" if atas_required is None else (
            "required" if atas_required else "not_required"
        ),
        "Required only where the sponsored research role meets ATAS conditions.",
        DOC_SOURCE
    )

    add(
        "translations",
        "Certified document translations",
        "verify" if translations_required is None else (
            "required" if translations_required else "not_required"
        ),
        "Required for supporting documents not written in English or Welsh.",
        DOC_SOURCE
    )

    add(
        "dependants",
        "Evidence of family relationships",
        "required" if dependants else "not_required",
        "Required when a partner or children apply as dependants.",
        DOC_SOURCE
    )

    add(
        "scholarship",
        "Government scholarship consent",
        "verify" if scholarship_consent is None else (
            "required" if scholarship_consent else "not_required"
        ),
        "Written consent may be required for certain recent government or international scholarship awards.",
        RULES_SOURCE
    )

    add(
        "identity",
        "Identity and biometrics verification",
        "verify",
        "Follow the identity verification instructions provided during the application.",
        RULES_SOURCE
    )

    return {
        "items": items,
        "maintenance_amount": MAINTENANCE if funds_required else Decimal("0"),
        "required": [
            item["code"] for item in items
            if item["status"] == "required"
        ],
        "to_verify": [
            item["code"] for item in items
            if item["status"] in ("verify", "may_be_requested")
        ],
    }
