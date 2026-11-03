LICENCE_SOURCE = (
    "https://www.gov.uk/uk-visa-sponsorship-employers/"
    "apply-for-your-licence"
)

LICENCE_PRIORITY_SOURCE = (
    "https://www.gov.uk/government/publications/"
    "pre-licence-priority-service-guidance/"
    "pre-licence-priority-service-guidance"
)

COS_SOURCE = (
    "https://www.gov.uk/uk-visa-sponsorship-employers/"
    "certificates-of-sponsorship"
)

COS_PRIORITY_SOURCE = (
    "https://www.gov.uk/government/publications/"
    "priority-change-of-circumstances-for-sponsors/"
    "tier-2-and-5-priority-change-of-circumstance-service"
)

VISA_SOURCE = (
    "https://www.gov.uk/senior-specialist-worker-visa"
)

PRIORITY_SOURCE = (
    "https://www.gov.uk/faster-decision-visa-settlement"
)

ETA_SOURCE = "https://www.gov.uk/eta/apply"


# Build the immigration processing timeline
def immigration_timeline(
    licence_status="existing",
    licence_priority=False,
    extra_cos_needed=False,
    cos_priority=False,
    location="outside",
    priority="none",
    eta_needed=False
):
    if licence_status not in ("existing", "new", "add_worker"):
        raise ValueError("Invalid sponsor licence status.")

    if location not in ("inside", "outside"):
        raise ValueError("Invalid visa application location.")

    if priority not in ("none", "priority", "super"):
        raise ValueError("Invalid visa priority option.")

    flags = (
        licence_priority,
        extra_cos_needed,
        cos_priority,
        eta_needed,
    )

    if any(type(value) is not bool for value in flags):
        raise ValueError("Invalid timeline option.")

    if licence_priority and licence_status != "new":
        raise ValueError("Licence priority requires a new licence.")

    if cos_priority and not extra_cos_needed:
        raise ValueError("CoS priority requires an additional allocation.")

    stages = []
    visitor_stages = []

    def add(items, code, title, time, source, note):
        items.append({
            "code": code,
            "title": title,
            "time": time,
            "source": source,
            "note": note,
        })

    # Include licence processing only where required
    if licence_status == "new":
        if licence_priority:
            licence_time = "Within 10 working days"
            licence_source = LICENCE_PRIORITY_SOURCE
        else:
            licence_time = "Most applications in less than 8 weeks"
            licence_source = LICENCE_SOURCE

        add(
            stages,
            "licence",
            "Sponsor Licence Application",
            licence_time,
            licence_source,
            "Priority depends on availability and eligibility. "
            "Additional checks can delay a decision."
        )

    elif licence_status == "add_worker":
        add(
            stages,
            "licence",
            "Sponsor Licence Route Addition",
            "Processing time requires verification",
            LICENCE_SOURCE,
            "The existing licence must be authorised for "
            "the Senior or Specialist Worker route."
        )

    # Request additional Undefined CoS allocation if necessary
    if extra_cos_needed:
        if cos_priority:
            cos_time = "Within 5 working days"
            cos_source = COS_PRIORITY_SOURCE
        else:
            cos_time = "Usually within 12 weeks"
            cos_source = COS_SOURCE

        add(
            stages,
            "allocation",
            "Additional Undefined CoS Allocation",
            cos_time,
            cos_source,
            "Priority is available only for eligible requests "
            "and does not guarantee approval."
        )

    add(
        stages,
        "certificate",
        "Assign Certificate of Sponsorship",
        "No fixed published processing time",
        COS_SOURCE,
        "The sponsor must have an available Undefined CoS. "
        "The worker must apply within three months of assignment."
    )

    # Determine visa processing time
    if priority == "priority":
        visa_time = "Usually within 5 working days"
        visa_source = PRIORITY_SOURCE

    elif priority == "super":
        visa_time = "Usually by the next working day"
        visa_source = PRIORITY_SOURCE

    elif location == "outside":
        visa_time = "Usually within 3 weeks"
        visa_source = VISA_SOURCE

    else:
        visa_time = "Usually within 8 weeks"
        visa_source = VISA_SOURCE

    add(
        stages,
        "visa",
        "Senior or Specialist Worker Visa Decision",
        visa_time,
        visa_source,
        "Processing normally begins after the application, "
        "identity verification and required documents. "
        "Faster services depend on availability."
    )

    # Assess ETA separately from the work visa timeline
    if eta_needed:
        add(
            visitor_stages,
            "eta",
            "Pre-Assignment Business Visit ETA",
            "Usually within 1 day; allow up to 3 working days",
            ETA_SOURCE,
            "An approved ETA is required before travelling "
            "for the qualifying business visit."
        )

    return {
        "route": "Senior or Specialist Worker",
        "location": location,
        "priority": priority,
        "licence_status": licence_status,
        "work_stages": stages,
        "visitor_stages": visitor_stages,
        "total_time": None,
        "total_status": "Cannot determine a guaranteed overall duration.",
        "application_rules": {
            "cos_valid_months": 3,
            "earliest_apply_months": 3,
            "source": COS_SOURCE,
        },
        "notes": [
            "Stages are shown in dependency order, not as "
            "a guaranteed total processing time.",
            "Document preparation, appointment availability "
            "and further checks may increase the timeline.",
            "CoS allocation is not the same as assigning a CoS.",
            "Priority services must be available and eligible "
            "before their processing times can be relied on.",
            "An ETA business visit is separate from obtaining "
            "permission for the UK employment assignment.",
        ],
    }
