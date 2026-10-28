from django.test import TestCase, SimpleTestCase
from decimal import Decimal
from estimator.services.currency import convert_currency


class CurrencyConversionTests(SimpleTestCase):

    # Convert annual salary from CHF to GBP
    def test_chf_to_gbp(self):
        result = convert_currency(
            "150000", "CHF", "GBP", "1.10"
        )
        self.assertEqual(
            result.quantize(Decimal("0.01")),
            Decimal("136363.64")
        )

    # Convert annual bonus from CHF to GBP
    def test_bonus_conversion(self):
        result = convert_currency(
            "20000", "CHF", "GBP", "1.10"
        )
        self.assertEqual(
            result.quantize(Decimal("0.01")),
            Decimal("18181.82")
        )

    # Convert relocation allowance
    def test_relocation_allowance(self):
        result = convert_currency(
            "5000", "CHF", "GBP", "1.10"
        )
        self.assertEqual(
            result.quantize(Decimal("0.01")),
            Decimal("4545.45")
        )

    # Convert another currency pair
    def test_usd_to_gbp(self):
        result = convert_currency(
            "100", "USD", "GBP", "1.25"
        )
        self.assertEqual(result, Decimal("80"))

    # Handle zero amount
    def test_zero_amount(self):
        result = convert_currency(
            "0", "CHF", "GBP", "1.10"
        )
        self.assertEqual(result, Decimal("0"))

    # Handle identical currencies
    def test_same_currency(self):
        result = convert_currency(
            "100", "GBP", "GBP", "1"
        )
        self.assertEqual(result, Decimal("100"))

    # Reject incorrect rate for identical currencies
    def test_same_currency_invalid_rate(self):
        with self.assertRaises(ValueError):
            convert_currency(
                "100", "GBP", "GBP", "1.20"
            )

    # Accept lowercase currency codes
    def test_lowercase_currency_codes(self):
        result = convert_currency(
            "100", "usd", "gbp", "1.25"
        )
        self.assertEqual(result, Decimal("80"))

    # Remove surrounding whitespace
    def test_currency_code_whitespace(self):
        result = convert_currency(
            "100", " USD ", " GBP ", "1.25"
        )
        self.assertEqual(result, Decimal("80"))

    # Reject zero exchange rate
    def test_zero_exchange_rate(self):
        with self.assertRaises(ValueError):
            convert_currency(
                "100", "CHF", "GBP", "0"
            )

    # Reject negative exchange rate
    def test_negative_exchange_rate(self):
        with self.assertRaises(ValueError):
            convert_currency(
                "100", "CHF", "GBP", "-1"
            )

    # Reject unsupported currency
    def test_unsupported_currency(self):
        with self.assertRaises(ValueError):
            convert_currency(
                "100", "XYZ", "GBP", "1.10"
            )

    # Reject malformed currency codes
    def test_invalid_currency_format(self):
        with self.assertRaises(ValueError):
            convert_currency(
                "100", "CH", "GBP", "1.10"
            )

    # Reject non-string currency codes
    def test_non_string_currency(self):
        with self.assertRaises(ValueError):
            convert_currency(
                "100", 123, "GBP", "1.10"
            )

    # Reject invalid monetary amount
    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            convert_currency(
                "hello", "CHF", "GBP", "1.10"
            )

    # Reject invalid exchange rate
    def test_invalid_exchange_rate(self):
        with self.assertRaises(ValueError):
            convert_currency(
                "100", "CHF", "GBP", "invalid"
            )

    # Reject non-finite numbers
    def test_non_finite_numbers(self):
        invalid_values = ["NaN", "Infinity", "-Infinity"]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    convert_currency(
                        value, "CHF", "GBP", "1.10"
                    )

                with self.assertRaises(ValueError):
                    convert_currency(
                        "100", "CHF", "GBP", value
                    )

    # Confirm the returned type is Decimal
    def test_return_type(self):
        result = convert_currency(
            "100", "USD", "GBP", "1.25"
        )
        self.assertIsInstance(result, Decimal)

    # Preserve decimal precision
    def test_decimal_precision(self):
        result = convert_currency(
            "1", "CHF", "GBP", "3"
        )
        self.assertEqual(
            result, Decimal("1") / Decimal("3")
        )
