from .eligibility import visa_checks
from .fees import visa_fees
from .documents import document_checks
from .visitor import visitor_checks
from .sponsorship import sponsor_checks
from .timeline import immigration_timeline


# Convert confirmation fields into Boolean or unknown values
def confirmed(value):
    options = {
        "yes": True,
        "no": False,
        "unknown": None,
    }

    if value not in options:
        raise ValueError("Invalid confirmation value.")

    return options[value]


# Combine the immigration assessments
def assess_immigration(data):
    licence_valid = confirmed(data["licence_valid"])

    if data["licence_status"] == "new":
        licence_valid = False

    sponsorship = sponsor_checks(
        licence_valid=licence_valid,
        route_authorised=confirmed(data["route_authorised"]),
        rating=data["rating"],
        continuing_same_route=data["continuing_same_route"],
        link_type=data["link_type"],
        link_verified=confirmed(data["link_verified"]),
        linked_entity_recorded=confirmed(data["linked_entity_recorded"]),
        genuine_job=confirmed(data["genuine_job"]),
        lawful_job=confirmed(data["lawful_job"]),
        cos_available=confirmed(data["cos_available"]),
        cos_assigned=confirmed(data["cos_assigned"]),
        cos_valid=confirmed(data["cos_valid"]),
        isc_paid=confirmed(data["isc_paid"]),
        isc_exempt=data["isc_exempt"],
    )

    sponsor_flags = {
        item["code"]: item["met"]
        for item in sponsorship["checks"]
    }

    eligibility = visa_checks(
        salary_chf=data["salary_chf"],
        rate=data["rate"],
        overseas_months=data["overseas_months"],
        weekly_hours=data["weekly_hours"],
        occupation_code=data["occupation_code"] or None,
        occupation_eligible=confirmed(data["occupation_eligible"]),
        going_rate_gbp=data["going_rate_gbp"],
        going_rate_hours=data["going_rate_hours"],
        allowed_allowance_chf=data["allowed_allowance_chf"],
        housing_allowance_chf=data["housing_allowance_chf"],
        sponsor_licensed=sponsor_flags["licence"],
        sponsor_a_rated=sponsor_flags["rating"],
        cos_valid=sponsor_flags["certificate"],
        corporate_link=sponsor_flags["corporate_link"],
        current_employee=confirmed(data["current_employee"]),
        genuine_job=sponsor_flags["genuine_job"],
        isc_compliant=sponsor_flags["isc"],
    )

    visitor = None

    if data["plan_visit"]:
        visitor = visitor_checks(
            purpose=data["purpose"],
            visit_months=data["visit_months"],
            passport_valid=data["passport_valid"],
            eta_exemption=data["eta_exemption"],
            has_valid_eta=data["has_valid_eta"],
        )

    eta_needed = (
        visitor is not None
        and visitor["eta_application_needed"] is True
    )

    fees = visa_fees(
        assignment_months=data["assignment_months"],
        permission_months=data["permission_months"],
        sponsor_size=data["sponsor_size"],
        location=data["location"],
        licence_status=data["licence_status"],
        isc_exempt=data["isc_exempt"],
        priority=data["priority"],
        eta=eta_needed,
        employer_pays_visa=data["employer_pays_visa"],
        employer_pays_ihs=data["employer_pays_ihs"],
        employer_pays_priority=data["employer_pays_priority"],
        employer_pays_eta=data["employer_pays_eta"],
        maintenance_certified=data["sponsor_maintenance"],
        licence_priority=data["licence_priority"],
        cos_priority=data["cos_priority"],
        extra_cos_needed=data["extra_cos_needed"],
    )

    documents = document_checks(
        eligible_salary_gbp=eligibility["general_salary"],
        uk_months=data["uk_months"],
        sponsor_maintenance=data["sponsor_maintenance"],
        tb_required=confirmed(data["tb_required"]),
        atas_required=confirmed(data["atas_required"]),
        dependants=data["dependants"],
        translations_required=confirmed(
            data["translations_required"]
        ),
        scholarship_consent=confirmed(
            data["scholarship_consent"]
        ),
    )

    timeline = immigration_timeline(
        licence_status=data["licence_status"],
        licence_priority=data["licence_priority"],
        extra_cos_needed=data["extra_cos_needed"],
        cos_priority=data["cos_priority"],
        location=data["location"],
        priority=data["priority"],
        eta_needed=eta_needed,
    )

    if eligibility["failed"]:
        status = "requirements_not_met"
    elif sponsorship["actions"]:
        status = "sponsorship_action_required"
    elif eligibility["pending"] or sponsorship["pending"]:
        status = "verification_required"
    else:
        status = "core_requirements_met"

    return {
        "status": status,
        "eligibility": eligibility,
        "sponsorship": sponsorship,
        "documents": documents,
        "visitor": visitor,
        "fees": fees,
        "timeline": timeline,
    }
