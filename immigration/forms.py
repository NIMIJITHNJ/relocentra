from decimal import Decimal
from django import forms

YES_NO = [
    ("unknown", "Not confirmed"),
    ("yes", "Yes"),
    ("no", "No"),
]


# Create a field for requirements needing confirmation
def confirm_field(label, initial="unknown"):
    return forms.ChoiceField(
        label=label,
        choices=YES_NO,
        initial=initial,
    )


class ImmigrationForm(forms.Form):

    # Assignment and salary details
    salary_chf = forms.DecimalField(
        label="Annual Base Salary (CHF)",
        initial=150000,
        min_value=0,
        max_digits=12,
        decimal_places=2,
    )

    rate = forms.DecimalField(
        label="Exchange Rate (CHF per GBP)",
        initial=Decimal("1.10"),
        min_value=Decimal("0.00000001"),
        max_digits=12,
        decimal_places=8,
    )

    overseas_months = forms.IntegerField(
        label="Overseas Employment (Months)",
        initial=36,
        min_value=0,
    )

    assignment_months = forms.IntegerField(
        label="Assignment Duration (Months)",
        initial=24,
        min_value=1,
        max_value=60,
    )

    permission_months = forms.DecimalField(
        label="Estimated Visa Permission (Months)",
        initial=Decimal("24.5"),
        min_value=Decimal("0.01"),
        max_digits=6,
        decimal_places=2,
        help_text="Illustrative permission period; confirm actual visa dates.",
    )

    weekly_hours = forms.DecimalField(
        label="Sponsored Weekly Working Hours",
        initial=Decimal("37.5"),
        min_value=Decimal("0.01"),
        max_digits=5,
        decimal_places=2,
    )

    # Occupation and eligible pay
    occupation_code = forms.RegexField(
        regex=r"^[0-9]{4}$",
        label="Occupation Code",
        required=False,
        help_text="Enter the verified four-digit occupation code.",
    )

    occupation_eligible = confirm_field(
        "Occupation Eligible for This Visa"
    )

    going_rate_gbp = forms.DecimalField(
        label="Occupation Going Rate (GBP)",
        required=False,
        min_value=Decimal("0.01"),
        max_digits=12,
        decimal_places=2,
    )

    going_rate_hours = forms.DecimalField(
        label="Going Rate Reference Hours",
        initial=Decimal("37.5"),
        min_value=Decimal("0.01"),
        max_digits=5,
        decimal_places=2,
    )

    allowed_allowance_chf = forms.DecimalField(
        label="Verified Qualifying Allowances (CHF)",
        initial=0,
        min_value=0,
        max_digits=12,
        decimal_places=2,
    )

    housing_allowance_chf = forms.DecimalField(
        label="Verified Qualifying Housing Allowance (CHF)",
        initial=0,
        min_value=0,
        max_digits=12,
        decimal_places=2,
    )

    current_employee = confirm_field(
        "Currently Employed by Overseas Business",
        "yes",
    )

    # Sponsor licence and corporate relationship
    licence_status = forms.ChoiceField(
        label="Sponsor Licence Position",
        choices=[
            ("existing", "Existing licence"),
            ("new", "New licence required"),
            ("add_worker", "Add Worker Route to Existing Licence"),
        ],
        initial="existing",
    )

    sponsor_size = forms.ChoiceField(
        label="Sponsor Organisation Size",
        choices=[
            ("small", "Small or Charitable Sponsor"),
            ("large", "Medium or Large Sponsor"),
        ],
        initial="large",
    )

    licence_valid = confirm_field("Valid Sponsor Licence")
    route_authorised = confirm_field("Correct GBM Route Authorised")

    rating = forms.ChoiceField(
        label="Sponsor Rating",
        choices=[
            ("unknown", "Not confirmed"),
            ("A", "A-rated"),
            ("B", "B-rated"),
            ("provisional", "Provisional"),
            ("none", "No rating"),
        ],
        initial="unknown",
    )

    continuing_same_route = forms.BooleanField(
        label="Continuing Existing Sponsorship Under Same Route",
        required=False,
    )

    link_type = forms.ChoiceField(
        label="Swiss–UK Corporate Relationship",
        choices=[
            ("unknown", "Not confirmed"),
            ("common_control", "Common Ownership or Control"),
            ("joint_venture", "Qualifying Joint Venture"),
            ("no_link", "No Qualifying Relationship"),
        ],
        initial="unknown",
    )

    link_verified = confirm_field("Corporate Link Verified")
    linked_entity_recorded = confirm_field(
        "Overseas Entity Recorded With UKVI"
    )

    genuine_job = confirm_field("Genuine Sponsored Job")
    lawful_job = confirm_field("Lawful Employment Terms")

    # Certificate of Sponsorship
    cos_available = confirm_field("Undefined CoS Allocation Available")
    cos_assigned = confirm_field("Certificate of Sponsorship Assigned")
    cos_valid = confirm_field("Certificate of Sponsorship Valid")
    isc_paid = confirm_field("Immigration Skills Charge Paid")

    isc_exempt = forms.BooleanField(
        label="Verified Immigration Skills Charge Exemption",
        required=False,
    )

    extra_cos_needed = forms.BooleanField(
        label="Additional CoS Allocation Required",
        required=False,
    )

    # Immigration application and fee options
    location = forms.ChoiceField(
        label="Visa Application Location",
        choices=[
            ("outside", "Outside the UK"),
            ("inside", "Inside the UK"),
        ],
        initial="outside",
    )

    priority = forms.ChoiceField(
        label="Visa Processing Service",
        choices=[
            ("none", "Standard"),
            ("priority", "Priority"),
            ("super", "Super Priority"),
        ],
        initial="none",
    )

    licence_priority = forms.BooleanField(
        label="Sponsor Licence Priority Service",
        required=False,
    )

    cos_priority = forms.BooleanField(
        label="Additional CoS Allocation Priority",
        required=False,
    )

    employer_pays_visa = forms.BooleanField(
        label="Employer Pays Visa Application Fee",
        required=False,
    )

    employer_pays_ihs = forms.BooleanField(
        label="Employer Pays Immigration Health Surcharge",
        required=False,
    )

    employer_pays_priority = forms.BooleanField(
        label="Employer Pays Visa Priority Fee",
        required=False,
    )

    employer_pays_eta = forms.BooleanField(
        label="Employer Pays ETA Fee",
        required=False,
    )

    # Pre-assignment business visit
    plan_visit = forms.BooleanField(
        label="Include a Pre-Assignment Business Visit",
        required=False,
        initial=True,
    )

    purpose = forms.ChoiceField(
        label="Business Visit Purpose",
        choices=[
            ("meetings", "Business Meetings"),
            ("conferences", "Conferences"),
            ("negotiations", "Contract Negotiations"),
            ("site_visit", "Site Visit"),
            ("training", "Training — Requires Review"),
            ("uk_employment", "Employment in UK"),
            ("other", "Other Activity"),
        ],
        initial="meetings",
    )

    visit_months = forms.DecimalField(
        label="Planned Business Visit Duration (Months)",
        initial=1,
        min_value=Decimal("0.01"),
        max_digits=5,
        decimal_places=2,
    )

    passport_valid = forms.TypedChoiceField(
        label="Valid Passport for Business Visit",
        choices=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        coerce=lambda value: value == "yes",
        initial="yes",
    )

    eta_exemption = forms.ChoiceField(
        label="ETA Exemption",
        choices=[
            ("none", "No Exemption"),
            ("uk_permission", "Existing UK Immigration Permission"),
            ("british_irish", "British or Irish Citizenship"),
            ("ireland_resident_cta", "Qualifying Irish Resident Travel"),
        ],
        initial="none",
    )

    has_valid_eta = forms.BooleanField(
        label="Already Holds a Valid ETA",
        required=False,
    )

    # Supporting documents and maintenance
    uk_months = forms.IntegerField(
        label="Prior Continuous UK Residence (Months)",
        initial=0,
        min_value=0,
    )

    sponsor_maintenance = forms.BooleanField(
        label="Sponsor Certifies Financial Maintenance",
        required=False,
    )

    tb_required = confirm_field("TB Test Required")
    atas_required = confirm_field("ATAS Certificate Required")
    translations_required = confirm_field(
        "Certified Translations Required"
    )

    scholarship_consent = confirm_field(
        "Government Scholarship Consent Required"
    )

    dependants = forms.BooleanField(
        label="Dependants Applying",
        required=False,
    )

    # Validate related input selections
    def clean(self):
        cleaned = super().clean()

        months = cleaned.get("assignment_months")
        permission = cleaned.get("permission_months")

        if months is not None and permission is not None:
            if permission < months:
                self.add_error(
                    "permission_months",
                    "Visa permission cannot be shorter than the assignment.",
                )

        if cleaned.get("licence_priority"):
            if cleaned.get("licence_status") != "new":
                self.add_error(
                    "licence_priority",
                    "Priority requires a new sponsor licence.",
                )

        if cleaned.get("cos_priority"):
            if not cleaned.get("extra_cos_needed"):
                self.add_error(
                    "cos_priority",
                    "Priority requires additional CoS allocation.",
                )

        if cleaned.get("cos_valid") == "yes":
            if cleaned.get("cos_assigned") != "yes":
                self.add_error(
                    "cos_valid",
                    "A valid CoS must already be assigned.",
                )

        return cleaned
