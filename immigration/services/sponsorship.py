GBM_SOURCE = (
    "https://www.gov.uk/government/publications/"
    "sponsor-a-global-business-mobility-worker"
)

RULES_SOURCE = (
    "https://www.gov.uk/guidance/immigration-rules/"
    "immigration-rules-appendix-global-business-mobility-routes"
)

COS_SOURCE = (
    "https://www.gov.uk/uk-visa-sponsorship-employers/"
    "certificates-of-sponsorship"
)

ISC_SOURCE = (
    "https://www.gov.uk/uk-visa-sponsorship-employers/"
    "immigration-skills-charge"
)

DUTIES_SOURCE = (
    "https://www.gov.uk/uk-visa-sponsorship-employers/"
    "your-responsibilities"
)

WORK_SOURCE = "https://www.gov.uk/check-job-applicant-right-to-work"

LINK_TYPES = {
    "unknown",
    "common_control",
    "joint_venture",
    "no_link",
}

RATINGS = {"A", "B", "provisional", "none", "unknown"}


# Validate confirmed, rejected or unknown conditions
def check_flag(value, name):
    if value is not None and type(value) is not bool:
        raise ValueError(f"Invalid {name}.")
    return value


# Assess employer sponsorship requirements
def sponsor_checks(
    licence_valid=None,
    route_authorised=None,
    rating="unknown",
    continuing_same_route=False,
    link_type="unknown",
    link_verified=None,
    linked_entity_recorded=None,
    genuine_job=None,
    lawful_job=None,
    cos_available=None,
    cos_assigned=None,
    cos_valid=None,
    isc_paid=None,
    isc_exempt=False,
):
    flags = {
        "licence status": licence_valid,
        "route authorisation": route_authorised,
        "overseas link evidence": link_verified,
        "linked entity registration": linked_entity_recorded,
        "genuine employment": genuine_job,
        "lawful employment terms": lawful_job,
        "CoS allocation": cos_available,
        "CoS assignment": cos_assigned,
        "CoS validity": cos_valid,
        "Immigration Skills Charge": isc_paid,
    }

    for name, value in flags.items():
        check_flag(value, name)

    if type(continuing_same_route) is not bool:
        raise ValueError("Invalid continuing sponsorship option.")

    if type(isc_exempt) is not bool:
        raise ValueError("Invalid ISC exemption option.")

    if rating not in RATINGS:
        raise ValueError("Invalid sponsor rating.")

    if link_type not in LINK_TYPES:
        raise ValueError("Invalid overseas business link.")

    if cos_valid is True and cos_assigned is not True:
        raise ValueError("A valid CoS must already be assigned.")

    # Check whether the sponsor rating is acceptable
    if rating == "A":
        rating_met = True
    elif rating == "B":
        rating_met = continuing_same_route
    elif rating == "unknown":
        rating_met = None
    else:
        rating_met = False

    # Check the qualifying overseas corporate relationship
    if link_type == "unknown":
        link_met = None
    elif link_type == "no_link":
        link_met = False
    else:
        link_met = link_verified

    # Check whether the CoS is ready for the application
    if cos_assigned is False:
        cos_met = False
    elif cos_assigned is None:
        cos_met = None
    else:
        cos_met = cos_valid

    # Apply a confirmed ISC exemption where applicable
    isc_met = True if isc_exempt else isc_paid

    requirements = [
        (
            "licence", "Valid sponsor licence",
            licence_valid, GBM_SOURCE,
        ),
        (
            "route", "Senior or Specialist Worker authorisation",
            route_authorised, GBM_SOURCE,
        ),
        (
            "rating", "Acceptable sponsor rating",
            rating_met, RULES_SOURCE,
        ),
        (
            "corporate_link", "Qualifying overseas business relationship",
            link_met, GBM_SOURCE,
        ),
        (
            "linked_entity", "Overseas business recorded with UKVI",
            linked_entity_recorded, GBM_SOURCE,
        ),
        (
            "genuine_job", "Genuine sponsored employment",
            genuine_job, GBM_SOURCE,
        ),
        (
            "lawful_job", "Lawful employment terms",
            lawful_job, GBM_SOURCE,
        ),
        (
            "allocation", "Available Undefined CoS allocation",
            cos_available, COS_SOURCE,
        ),
        (
            "certificate", "Valid assigned Certificate of Sponsorship",
            cos_met, COS_SOURCE,
        ),
        (
            "isc", "Immigration Skills Charge paid or exempt",
            isc_met, ISC_SOURCE,
        ),
    ]

    checks = []

    for code, title, met, source in requirements:
        if met is True:
            status = "met"
        elif met is False:
            status = "action_required"
        else:
            status = "verification_required"

        checks.append({
            "code": code,
            "title": title,
            "met": met,
            "status": status,
            "source": source,
        })

    actions = [
        item["code"] for item in checks
        if item["status"] == "action_required"
    ]

    pending = [
        item["code"] for item in checks
        if item["status"] == "verification_required"
    ]

    if actions:
        overall_status = "action_required"
    elif pending:
        overall_status = "verification_required"
    else:
        overall_status = "sponsorship_requirements_met"

    duties = [
        {
            "code": "right_to_work",
            "title": "Complete right-to-work checks before employment",
            "stage": "before_start",
            "source": WORK_SOURCE,
        },
        {
            "code": "records",
            "title": "Maintain required worker and sponsorship records",
            "stage": "ongoing",
            "source": DUTIES_SOURCE,
        },
        {
            "code": "attendance",
            "title": "Monitor attendance and maintain contact details",
            "stage": "ongoing",
            "source": DUTIES_SOURCE,
        },
        {
            "code": "worker_changes",
            "title": "Report relevant worker changes, normally within 10 working days",
            "stage": "ongoing",
            "source": DUTIES_SOURCE,
        },
        {
            "code": "organisation_changes",
            "title": "Report significant business changes, normally within 20 working days",
            "stage": "ongoing",
            "source": DUTIES_SOURCE,
        },
        {
            "code": "sponsor_fees",
            "title": "Pay sponsorship fees without recovering prohibited costs from the worker",
            "stage": "sponsorship",
            "source": GBM_SOURCE,
        },
    ]

    return {
        "route": "Senior or Specialist Worker",
        "cos_type": "undefined",
        "status": overall_status,
        "checks": checks,
        "actions": actions,
        "pending": pending,
        "duties": duties,
        "cos_rules": {
            "apply_within_months": 3,
            "earliest_application_months": 3,
            "source": COS_SOURCE,
        },
        "notes": [
            "The occupation, salary and overseas employment checks "
            "must also be satisfied.",
            "A B-rated sponsor exception applies only when "
            "continuing sponsorship under the relevant conditions.",
            "CoS validity includes timing, route, job details "
            "and other Home Office requirements.",
            "An ISC exemption must be independently verified.",
            "Meeting these checks does not guarantee visa approval.",
        ],
    }
