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
            ("employer_direct", "Paid Directly by Employer"),
            ("employee_direct", "Paid Directly to Employee"),
            ("reimbursed", "Reimbursed to Employee")
        ],
        initial="employer_direct",
        label="Relocation Expense Payment Method"
    )

    certificate = forms.BooleanField(
        required=False,
        initial=False,
        label="Valid Swiss Social Security Certificate Covers Both Years"
    )
