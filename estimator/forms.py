from django import forms
from decimal import Decimal

CURRENCY_CHOICES = [
    ("CHF", "CHF - Swiss Franc"),
    ("GBP", "GBP - British Pound"),
    ("USD", "USD - US Dollar"),
    ("EUR", "EUR - Euro"),
    ("INR", "INR - Indian Rupee"),
    ("AED", "AED - UAE Dirham"),
    ("SAR", "SAR - Saudi Riyal"),
    ("CAD", "CAD - Canadian Dollar"),
    ("AUD", "AUD - Australian Dollar"),
    ("JPY", "JPY - Japanese Yen"),
]


class CurrencyConversionForm(forms.Form):

    from_currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        initial="CHF",
        label="From Currency"
    )

    to_currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        initial="GBP",
        label="To Currency"
    )

    amount = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=150000,
        label="Amount"
    )

    exchange_rate = forms.DecimalField(
        min_value=Decimal("0.00000001"),
        max_digits=18,
        decimal_places=8,
        initial=Decimal("1.10"),
        label="Exchange Rate",
        help_text="Number of source currency units per 1 target currency unit."
    )

    def clean(self):
        cleaned_data = super().clean()

        source = cleaned_data.get("from_currency")
        target = cleaned_data.get("to_currency")
        rate = cleaned_data.get("exchange_rate")

        if source == target and rate is not None and rate != 1:
            self.add_error(
                "exchange_rate",
                "Exchange rate must be 1 for identical currencies."
            )

        return cleaned_data

class AssignmentCostForm(forms.Form):

    salary = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=150000,
        label="Annual Salary (CHF)"
    )

    bonus = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=20000,
        label="Annual Bonus (CHF)"
    )

    rate = forms.DecimalField(
        min_value=Decimal("0.00000001"),
        max_digits=18,
        decimal_places=8,
        initial=Decimal("1.10"),
        label="Exchange Rate (CHF per GBP)",
        help_text="For example, 1 GBP = 1.10 CHF."
    )

    swiss_tax = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=29578,
        label="Annual Swiss Hypothetical Income Tax (CHF)",
        help_text="Enter the Swiss tax estimate for the selected salary and circumstances."
    )

    monthly_rent = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=3000,
        label="Monthly UK Housing Cost (GBP)"
    )

    relocation = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=5000,
        label="One-Time Relocation Allowance (CHF)"
    )

    moving = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=6000,
        label="Moving Expenses (GBP)"
    )

    temporary = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=4000,
        label="Temporary Accommodation (GBP)"
    )

    taxable_kind1 = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=36000,
        label="Year 1 Taxable Accommodation and Other Benefits (GBP)",
        help_text="Exclude relocation expenses calculated separately."
    )

    taxable_kind2 = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=36000,
        label="Year 2 Taxable Accommodation and Other Benefits (GBP)",
        help_text="Exclude relocation expenses calculated separately."
    )

    moving_ok = forms.BooleanField(
        required=False,
        initial=False,
        label="Moving Expenses Qualify for Relocation Exemption"
    )

    temporary_ok = forms.BooleanField(
        required=False,
        initial=False,
        label="Temporary Accommodation Qualifies for Relocation Exemption"
    )
    
    payment = forms.ChoiceField(
        choices=[
            (
                "employer_direct",
                "Employer Arranges and Pays Supplier"
            ),
            (
                "employee_direct",
                "Employee Arranges, Employer Pays Supplier"
            ),
            (
                "reimbursed",
                "Employee Pays, Employer Reimburses"
            )
        ],
        initial="employer_direct",
        label="Relocation Expense Payment Method"
    )

    certificate = forms.BooleanField(
        required=False,
        initial=False,
        label="Valid Swiss Social Security Certificate Covers Both Years"
    )
    
    additional_chf1 = forms.DecimalField(
        label="Year 1 Additional Swiss Employer Costs (CHF)",
        min_value=0,
        initial=0,
        required=False,
        max_digits=12,
        decimal_places=2
    )

    additional_chf2 = forms.DecimalField(
        label="Year 2 Additional Swiss Employer Costs (CHF)",
        min_value=0,
        initial=0,
        required=False,
        max_digits=12,
        decimal_places=2
    )

class AccommodationAssessmentForm(forms.Form):

    annual_value = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        label="HMRC Annual Accommodation Value (GBP)",
        help_text="Use the applicable statutory annual value, not the property's market price."
    )

    property_cost = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        label="Qualifying Property Provision Cost (GBP)",
        help_text="Relevant acquisition or lease-related cost, not annual rent or market value."
    )

    interest_rate = forms.DecimalField(
        min_value=Decimal("0"),
        max_value=Decimal("1"),
        max_digits=10,
        decimal_places=6,
        label="Applicable Official Interest Rate",
        help_text="Enter as a decimal, for example 0.0375 for 3.75%."
    )

    employee_rent = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=0,
        label="Annual Employee Rent Contribution (GBP)"
    )

    employer_recovery = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=0,
        label="Annual Housing Payment Recovered by Employer (GBP)"
    )

    relief = forms.DecimalField(
        min_value=Decimal("0"),
        max_digits=18,
        decimal_places=2,
        initial=0,
        label="Assessed Accommodation Tax Relief (GBP)"
    )

    employment = forms.ChoiceField(
        choices=[
            ("unknown", "Not Confirmed"),
            ("continuing", "Continuing Employment"),
            ("new", "New Employment Arrangement")
        ],
        initial="unknown",
        label="Employment Arrangement"
    )

    temporary_purpose = forms.ChoiceField(
        choices=[
            ("unknown", "Not Confirmed"),
            ("yes", "Yes"),
            ("no", "No")
        ],
        initial="unknown",
        label="Temporary Workplace Purpose"
    )

    expected_months = forms.IntegerField(
        min_value=1,
        initial=24,
        label="Expected UK Assignment Duration (Months)"
    )

    work_percent = forms.DecimalField(
        min_value=Decimal("0"),
        max_value=Decimal("100"),
        max_digits=5,
        decimal_places=2,
        initial=100,
        label="Percentage of Working Time at UK Workplace"
    )

    additional_cost = forms.ChoiceField(
        choices=[
            ("unknown", "Not Confirmed"),
            ("yes", "Yes"),
            ("no", "No")
        ],
        initial="unknown",
        label="Accommodation Cost Attributable to Business Travel"
    )

    reasonable_cost = forms.ChoiceField(
        choices=[
            ("unknown", "Not Confirmed"),
            ("yes", "Yes"),
            ("no", "No")
        ],
        initial="unknown",
        label="Accommodation Cost Confirmed as Reasonable"
    )

    relief_verified = forms.BooleanField(
        required=False,
        initial=False,
        label="Relief Eligibility Supported by Evidence"
    )
    
    # Prepare validated accommodation inputs for the calculation engine
    def housing_data(self):
        if not self.is_valid():
            raise ValueError("Accommodation form contains invalid inputs.")

        data = self.cleaned_data

        choices = {
            "yes": True,
            "no": False,
            "unknown": None
        }

        return {
            "annual_value": data["annual_value"],
            "property_cost": data["property_cost"],
            "interest_rate": data["interest_rate"],
            "employee_rent": data["employee_rent"],
            "employer_recovery": data["employer_recovery"],
            "relief": data["relief"],
            "relief_verified": data["relief_verified"],
            "assignment": {
                "employment": data["employment"],
                "temporary_purpose": choices[data["temporary_purpose"]],
                "expected_months": data["expected_months"],
                "work_percent": data["work_percent"],
                "additional_cost": choices[data["additional_cost"]],
                "reasonable_cost": choices[data["reasonable_cost"]]
            }
        }
