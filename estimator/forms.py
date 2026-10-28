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