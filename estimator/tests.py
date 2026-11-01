from django.test import TestCase, SimpleTestCase
from decimal import Decimal
from estimator.services.currency import convert_currency
from estimator.services.uk_tax import personal_allowance
from estimator.services.uk_tax import personal_allowance, uk_incometax
from estimator.services.gross_up import tax_grossup
from estimator.services.swiss_tax import swiss_incometax
from estimator.services.social_security import employee_social, employer_social, coverage_status, uk_employer_ni, uk_class1a_ni, uk_ni_charges, ni_scenario
from estimator.services.benefits import relocation_relief, housing_cost, housing_tax, relocation_cash, benefit_values, relocation_split, relocation_tax
from estimator.services.cost_estimate import year_cost, assignment_total, home_pay, hypo_deductions, year_benefits, grossup_base, host_tax, swiss_charges, estimate_year, estimate_assignment

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

    
class PersonalAllowanceTests(SimpleTestCase):

    # Check personal allowance at different income levels
    def test_personal_allowance(self):
        test_cases = [
            ("50000", "12570"),
            ("100000", "12570"),
            ("110000", "7570"),
            ("120000", "2570"),
            ("125140", "0"),
            ("150000", "0"),
        ]

        for income, expected in test_cases:
            with self.subTest(income=income):
                result = personal_allowance(income)
                self.assertEqual(result, Decimal(expected))


class IncomeTaxTests(SimpleTestCase):

    # Test UK income tax at different income levels
    def test_uk_incometax(self):
        test_cases = [
            ("0", "0"),
            ("12570", "0"),
            ("50000", "7486"),
            ("100000", "27432"),
            ("110000", "33432"),
            ("125140", "42516"),
            ("150000", "53703"),
        ]

        for income, expected in test_cases:
            with self.subTest(income=income):
                result = uk_incometax(income)
                self.assertEqual(result, Decimal(expected))

class GrossUpTests(SimpleTestCase):

    # Test the gross-up calculation against the expected tax
    def test_grossup(self):
        tax = tax_grossup("30000")

        self.assertEqual(
            tax.quantize(Decimal("0.01")),
            Decimal("4357.50")
        )

        self.assertLess(
            abs(tax - uk_incometax(Decimal("30000") + tax)),
            Decimal("0.01")
        )

    # Check gross-up when taxable income is zero
    def test_zero_income(self):
        result = tax_grossup("0")
        self.assertEqual(result, Decimal("0"))

    # Test gross-up for income in the additional tax band
    def test_high_income(self):
        income = Decimal("150000")
        tax = tax_grossup(income)

        expected_tax = uk_incometax(income + tax)

        self.assertGreater(tax, Decimal("0"))
        self.assertLess(
            abs(tax - expected_tax),
            Decimal("0.01")
        )

    # Check the final gross-up amount for high income
    def test_high_income_amount(self):
        tax = tax_grossup("150000")

        self.assertEqual(
        tax.quantize(Decimal("0.01")),
        Decimal("97641.82")
    )


class SwissTaxTests(SimpleTestCase):

    # Check Swiss income tax against the official Zurich estimate
    def test_zurich_tax(self):
        result = swiss_incometax(
            "6735", "10130", "12689", "24"
        )

        self.assertEqual(result, Decimal("29578"))

class SocialSecurityTests(SimpleTestCase):

    # Test Swiss employee contributions for CHF 170,000
    def test_employee_social(self):
        result = employee_social("170000")

        self.assertEqual(result["ahv"], Decimal("9010.00"))
        self.assertEqual(result["alv"], Decimal("1630.20"))
        self.assertEqual(result["total"], Decimal("10640.20"))

    # Test Swiss employer contributions for CHF 170,000
    def test_employer_social(self):
        result = employer_social("170000")

        self.assertEqual(result["ahv"], Decimal("9010.00"))
        self.assertEqual(result["alv"], Decimal("1630.20"))
        self.assertEqual(result["total"], Decimal("10640.20"))
    
    # Check the unemployment contribution ceiling
    def test_alv_limit(self):
        test_cases = [
            ("100000", "1100.00"),
            ("148200", "1630.20"),
            ("170000", "1630.20"),
            ("200000", "1630.20"),
        ]

        for income, expected in test_cases:
            with self.subTest(income=income):
                result = employee_social(income)
                self.assertEqual(result["alv"], Decimal(expected))
    
    # Test confirmed and unverified Swiss social security coverage
    def test_coverage_status(self):
        confirmed = coverage_status(True)

        self.assertEqual(confirmed["country"], "Switzerland")
        self.assertFalse(confirmed["uk_ni"])
        self.assertEqual(confirmed["status"], "Swiss coverage confirmed")

        unverified = coverage_status(False)

        self.assertIsNone(unverified["country"])
        self.assertIsNone(unverified["uk_ni"])
        self.assertEqual(unverified["status"], "Coverage requires verification")

    # Check invalid certificate status inputs
    def test_coverage_invalid(self):
        for value in ("yes", "no", 1, 0, None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    coverage_status(value)
    
    # Test standard UK employer National Insurance calculations
    def test_uk_employer_ni(self):
        self.assertEqual(
            uk_employer_ni("3000", "417"),
            Decimal("387.45")
        )

        self.assertEqual(
            uk_employer_ni("60000", "5000"),
            Decimal("8250.00")
        )

        self.assertEqual(
            uk_employer_ni("4000", "5000"),
            Decimal("0")
        )

    # Test invalid UK employer National Insurance inputs
    def test_uk_employer_ni_invalid(self):
        invalid = [
            ("-100", "417"),
            ("3000", "-417"),
            ("NaN", "417"),
            ("Infinity", "417")
        ]

        for earnings, threshold in invalid:
            with self.subTest(earnings=earnings, threshold=threshold):
                with self.assertRaises(ValueError):
                    uk_employer_ni(earnings, threshold)
    
    # Test UK employer Class 1A National Insurance
    def test_uk_class1a_ni(self):
        self.assertEqual(
            uk_class1a_ni("2000"),
            Decimal("300.00")
        )

        self.assertEqual(
            uk_class1a_ni("36000"),
            Decimal("5400.00")
        )

        self.assertEqual(
            uk_class1a_ni("0"),
            Decimal("0.00")
        )

    # Test invalid Class 1A benefit values
    def test_uk_class1a_ni_invalid(self):
        for value in ("-100", "NaN", "Infinity"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    uk_class1a_ni(value)
    
    # Test combined UK employer National Insurance
    def test_uk_ni_charges(self):
        result = uk_ni_charges("60000", "2000", "5000")

        self.assertEqual(result["class1"], Decimal("8250.00"))
        self.assertEqual(result["class1a"], Decimal("300.00"))
        self.assertEqual(result["total"], Decimal("8550.00"))

        below = uk_ni_charges("4000", "1000", "5000")

        self.assertEqual(below["class1"], Decimal("0"))
        self.assertEqual(below["class1a"], Decimal("150.00"))
        self.assertEqual(below["total"], Decimal("150.00"))

    # Test invalid combined National Insurance inputs
    def test_uk_ni_charges_invalid(self):
        invalid = [
            ("-100", "2000", "5000"),
            ("60000", "-200", "5000"),
            ("60000", "2000", "-5000"),
            ("NaN", "2000", "5000")
        ]

        for earnings, benefits, threshold in invalid:
            with self.subTest(earnings=earnings, benefits=benefits):
                with self.assertRaises(ValueError):
                    uk_ni_charges(earnings, benefits, threshold)
    
    # Test UK National Insurance under different coverage scenarios
    def test_ni_scenario(self):
        confirmed = ni_scenario("60000", "2000", "5000", certificate=True)

        self.assertFalse(confirmed["applicable"])
        self.assertEqual(confirmed["liability"], Decimal("0"))
        self.assertIsNone(confirmed["illustrative"])

        unverified = ni_scenario("60000", "2000", "5000", certificate=False)

        self.assertIsNone(unverified["applicable"])
        self.assertIsNone(unverified["liability"])

        self.assertEqual(
            unverified["illustrative"]["class1"],
            Decimal("8250.00")
        )

        self.assertEqual(
            unverified["illustrative"]["class1a"],
            Decimal("300.00")
        )

        self.assertEqual(
            unverified["illustrative"]["total"],
            Decimal("8550.00")
        )

    # Test invalid inputs for National Insurance scenarios
    def test_ni_scenario_invalid(self):
        with self.assertRaises(ValueError):
            ni_scenario("60000", "2000", "5000", certificate="yes")

        with self.assertRaises(ValueError):
            ni_scenario("-100", "2000", "5000", certificate=False)

        with self.assertRaises(ValueError):
            ni_scenario("60000", "-2000", "5000", certificate=False)

class BenefitsTests(SimpleTestCase):

    # Test relocation relief for different eligibility conditions
    def test_relocation_relief(self):
        test_cases = [
            (True, True, "8000", "2000"),
            (True, False, "6000", "4000"),
            (False, True, "4000", "6000"),
            (False, False, "0", "10000"),
        ]

        for moving_ok, temporary_ok, exempt, non_exempt in test_cases:
            with self.subTest(moving=moving_ok, temporary=temporary_ok):
                result = relocation_relief(
                    "6000", "4000", moving_ok, temporary_ok
                )

                self.assertEqual(result["total"], Decimal("10000"))
                self.assertEqual(result["exempt"], Decimal(exempt))
                self.assertEqual(result["non_exempt"], Decimal(non_exempt))
    
    # Check the maximum relocation exemption
    def test_relocation_limit(self):
        result = relocation_relief("8000", "5000", True, True)

        self.assertEqual(result["total"], Decimal("13000"))
        self.assertEqual(result["exempt"], Decimal("8000"))
        self.assertEqual(result["non_exempt"], Decimal("5000"))

    # Check invalid relocation expenses and eligibility
    def test_relocation_invalid(self):
        invalid_cases = [
            ("-100", "4000", True, True),
            ("6000", "-500", True, True),
            ("invalid", "4000", True, True),
            ("NaN", "4000", True, True),
            ("6000", "4000", "yes", True),
        ]

        for moving, temporary, moving_ok, temporary_ok in invalid_cases:
            with self.subTest(moving=moving, temporary=temporary):
                with self.assertRaises(ValueError):
                    relocation_relief(
                        moving, temporary, moving_ok, temporary_ok
                    )
    
    # Check housing costs for different rental periods
    def test_housing_cost(self):
        test_cases = [
            ("3000", 12, "36000"),
            ("3000", 6, "18000"),
            ("3000", 1, "3000"),
            ("3000", 0, "0"),
            ("0", 12, "0"),
        ]

        for rent, months, expected in test_cases:
            with self.subTest(rent=rent, months=months):
                result = housing_cost(rent, months)
                self.assertEqual(result, Decimal(expected))
    
    # Check invalid housing costs and rental periods
    def test_housing_invalid(self):
        invalid_cases = [
            ("-3000", 12),
            ("invalid", 12),
            ("NaN", 12),
            ("Infinity", 12),
            ("3000", -1),
            ("3000", 2.5),
            ("3000", True),
            ("3000", "12"),
        ]

        for rent, months in invalid_cases:
            with self.subTest(rent=rent, months=months):
                with self.assertRaises(ValueError):
                    housing_cost(rent, months)
    
    # Test taxable housing benefits with different relief amounts
    def test_housing_tax(self):
        test_cases = [
            ("36000", "0", "36000"),
            ("36000", "12000", "24000"),
            ("36000", "36000", "0"),
            ("0", "0", "0"),
        ]

        for gross, relief, expected in test_cases:
            with self.subTest(gross=gross, relief=relief):
                result = housing_tax(gross, relief)

                self.assertEqual(result["gross"], Decimal(gross))
                self.assertEqual(result["relief"], Decimal(relief))
                self.assertEqual(result["taxable"], Decimal(expected))
    
    # Check invalid housing benefits and relief amounts
    def test_housing_tax_invalid(self):
        invalid_cases = [
            ("-1000", "0"),
            ("36000", "-500"),
            ("36000", "40000"),
            ("invalid", "0"),
            ("36000", "invalid"),
            ("NaN", "0"),
            ("36000", "Infinity"),
            (None, "0"),
        ]

        for gross, relief in invalid_cases:
            with self.subTest(gross=gross, relief=relief):
                with self.assertRaises(ValueError):
                    housing_tax(gross, relief)
    
    # Test relocation cash allowance conversion
    def test_relocation_cash(self):
        test_cases = [
            ("5000", "CHF", "1.10", "4545.45"),
            ("1000", "GBP", "1", "1000.00"),
            ("0", "CHF", "1.10", "0.00"),
        ]

        for amount, currency, rate, expected in test_cases:
            with self.subTest(currency=currency, amount=amount):
                result = relocation_cash(amount, currency, rate)

                self.assertEqual(
                    result["cost"].quantize(Decimal("0.01")),
                    Decimal(expected)
                )
                self.assertEqual(
                    result["taxable_cash"],
                    result["cost"]
                )

    # Check invalid relocation allowance inputs
    def test_relocation_cash_invalid(self):
        invalid_cases = [
            ("-5000", "CHF", "1.10"),
            ("invalid", "CHF", "1.10"),
            ("5000", "XYZ", "1.10"),
            ("5000", "CHF", "0"),
            ("NaN", "CHF", "1.10"),
        ]

        for amount, currency, rate in invalid_cases:
            with self.subTest(amount=amount, currency=currency):
                with self.assertRaises(ValueError):
                    relocation_cash(amount, currency, rate)
    
    # Test taxable cash and benefits in kind
    def test_benefit_values(self):
        result = benefit_values("4545.45", "36000")

        self.assertEqual(result["taxable_cash"], Decimal("4545.45"))
        self.assertEqual(result["taxable_kind"], Decimal("36000"))
        self.assertEqual(result["total_taxable"], Decimal("40545.45"))

    # Check invalid taxable benefit amounts
    def test_benefit_values_invalid(self):
        invalid_cases = [
            ("-100", "36000"),
            ("4545", "-500"),
            ("invalid", "36000"),
            ("NaN", "36000"),
            ("4545", "Infinity"),
            (None, "36000"),
        ]

        for cash, kind in invalid_cases:
            with self.subTest(cash=cash, kind=kind):
                with self.assertRaises(ValueError):
                    benefit_values(cash, kind)
    
    # Test relocation exemption allocation for different eligibility conditions
    def test_relocation_split(self):
        test_cases = [
            (True, True, "6000", "2000", "2000"),
            (True, False, "6000", "0", "4000"),
            (False, True, "0", "4000", "6000"),
            (False, False, "0", "0", "10000"),
        ]

        for moving_ok, temporary_ok, moving_exempt, temporary_exempt, non_exempt in test_cases:
            with self.subTest(moving=moving_ok, temporary=temporary_ok):
                result = relocation_split(
                    "6000", "4000", moving_ok, temporary_ok
                )

                self.assertEqual(
                    result["moving_exempt"], Decimal(moving_exempt)
                )
                self.assertEqual(
                    result["temporary_exempt"], Decimal(temporary_exempt)
                )
                self.assertEqual(
                    result["total_non_exempt"], Decimal(non_exempt)
                )
                self.assertEqual(
                    result["total_exempt"] + result["total_non_exempt"],
                    Decimal("10000")
                )
    
    # Test qualifying excess and non-qualifying relocation expenses
    def test_relocation_classification(self):
        test_cases = [
            (True, True, "2000", "0"),
            (True, False, "0", "4000"),
            (False, True, "0", "6000"),
            (False, False, "0", "10000"),
        ]

        for moving_ok, temporary_ok, excess, non_qualifying in test_cases:
            with self.subTest(moving=moving_ok, temporary=temporary_ok):
                result = relocation_split(
                    "6000", "4000", moving_ok, temporary_ok
                )

                self.assertEqual(
                    result["qualifying_excess"], Decimal(excess)
                )

                self.assertEqual(
                    result["non_qualifying"], Decimal(non_qualifying)
                )

                self.assertEqual(
                    result["total_non_exempt"],
                    result["qualifying_excess"] + result["non_qualifying"]
                )
    
    # Test relocation tax classification for different payment methods
    def test_relocation_tax(self):
        relief = relocation_split("9000", "4000", True, False)

        test_cases = [
            ("employer_direct", "0", "5000"),
            ("employee_direct", "0", "5000"),
            ("reimbursed", "4000", "1000"),
        ]

        for payment, cash, kind in test_cases:
            with self.subTest(payment=payment):
                result = relocation_tax(relief, payment)

                self.assertEqual(
                    result["taxable_cash"], Decimal(cash)
                )
                self.assertEqual(
                    result["taxable_kind"], Decimal(kind)
                )
                self.assertEqual(
                    result["total_taxable"], Decimal("5000")
                )
                self.assertEqual(result["payment_method"], payment)
    
    # Test relocation reporting and National Insurance classifications
    def test_relocation_reporting(self):
        relief = relocation_split("9000", "4000", True, False)

        test_cases = [
            ("employer_direct", "0", "5000", "0", "5000"),
            ("employee_direct", "0", "5000", "4000", "1000"),
            ("reimbursed", "4000", "1000", "4000", "1000"),
        ]

        for payment, paye, p11d, class1, class1a in test_cases:
            with self.subTest(payment=payment):
                result = relocation_tax(relief, payment)

                self.assertEqual(result["paye_value"], Decimal(paye))
                self.assertEqual(result["p11d_value"], Decimal(p11d))
                self.assertEqual(result["uk_class1_base"], Decimal(class1))
                self.assertEqual(result["uk_class1a_base"], Decimal(class1a))

class EmployerCostTests(SimpleTestCase):

    # Check annual employer cost with deductions and charges
    def test_year_cost(self):
        result = year_cost(
            home_pay="150000",
            benefits="50000",
            host_tax="40000",
            employer_charges="10000",
            hypo_tax="20000",
            hypo_social="10000"
        )

        self.assertEqual(result["home_pay"], Decimal("150000"))
        self.assertEqual(result["benefits"], Decimal("50000"))
        self.assertEqual(result["host_tax"], Decimal("40000"))
        self.assertEqual(result["employer_charges"], Decimal("10000"))
        self.assertEqual(result["hypo_tax"], Decimal("20000"))
        self.assertEqual(result["hypo_social"], Decimal("10000"))
        self.assertEqual(result["total"], Decimal("220000"))
    
    # Check invalid employer cost inputs
    def test_year_cost_invalid(self):
        invalid_cases = [
            ("-100", "50000", "40000", "10000", "20000", "10000"),
            ("150000", "-500", "40000", "10000", "20000", "10000"),
            ("150000", "50000", "invalid", "10000", "20000", "10000"),
            ("150000", "50000", "40000", "NaN", "20000", "10000"),
            ("150000", "50000", "40000", "10000", "Infinity", "10000"),
            ("150000", "50000", "40000", "10000", "20000", None),
        ]

        for values in invalid_cases:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    year_cost(*values)
    
    # Test the combined employer cost for a two-year assignment
    def test_assignment_total(self):
        year1 = year_cost(
            "150000", "50000", "40000",
            "10000", "20000", "10000"
        )

        year2 = year_cost(
            "150000", "36000", "40000",
            "10000", "20000", "10000"
        )

        result = assignment_total(year1, year2)

        self.assertEqual(result["year1"], Decimal("220000"))
        self.assertEqual(result["year2"], Decimal("206000"))
        self.assertEqual(result["total"], Decimal("426000"))
        self.assertEqual(result["home_pay"], Decimal("300000"))
        self.assertEqual(result["multiple"], Decimal("1.42"))
    
    # Check assignment cost when home pay is zero
    def test_zero_home_pay(self):
        year1 = year_cost("0", "5000", "0", "0", "0", "0")
        year2 = year_cost("0", "3000", "0", "0", "0", "0")

        result = assignment_total(year1, year2)

        self.assertEqual(result["year1"], Decimal("5000"))
        self.assertEqual(result["year2"], Decimal("3000"))
        self.assertEqual(result["total"], Decimal("8000"))
        self.assertEqual(result["home_pay"], Decimal("0"))
        self.assertIsNone(result["multiple"])
    
    # Test annual home salary and bonus conversion
    def test_home_pay(self):
        result = home_pay("150000", "20000", "CHF", "1.10")

        self.assertEqual(
            result["salary"].quantize(Decimal("0.01")),
            Decimal("136363.64")
        )

        self.assertEqual(
            result["bonus"].quantize(Decimal("0.01")),
            Decimal("18181.82")
        )

        self.assertEqual(
            result["total"].quantize(Decimal("0.01")),
            Decimal("154545.45")
        )

        self.assertEqual(
            result["total"],
            result["salary"] + result["bonus"]
        )
    
    # Test hypothetical Swiss deductions converted into GBP
    def test_hypo_deductions(self):
        result = hypo_deductions("29578", "10640.20", "1.10")

        self.assertEqual(
            result["hypo_tax"].quantize(Decimal("0.01")),
            Decimal("26889.09")
        )

        self.assertEqual(
            result["hypo_social"].quantize(Decimal("0.01")),
            Decimal("9672.91")
        )

        self.assertEqual(
            result["total"].quantize(Decimal("0.01")),
            Decimal("36562.00")
        )

        self.assertEqual(
            result["total"],
            result["hypo_tax"] + result["hypo_social"]
        )
    
    # Test assignment benefits for both years
    def test_year_benefits(self):
        year1 = year_benefits(1, "3000", "5000", "6000", "4000", "1.10")
        year2 = year_benefits(2, "3000", "5000", "6000", "4000", "1.10")

        self.assertEqual(year1["housing"], Decimal("36000"))
        self.assertEqual(
            year1["relocation"].quantize(Decimal("0.01")),
            Decimal("4545.45")
        )
        self.assertEqual(year1["moving"], Decimal("6000"))
        self.assertEqual(year1["temporary"], Decimal("4000"))
        self.assertEqual(
            year1["total"].quantize(Decimal("0.01")),
            Decimal("50545.45")
        )

        self.assertEqual(year2["housing"], Decimal("36000"))
        self.assertEqual(year2["relocation"], Decimal("0"))
        self.assertEqual(year2["moving"], Decimal("0"))
        self.assertEqual(year2["temporary"], Decimal("0"))
        self.assertEqual(year2["total"], Decimal("36000"))
    
    # Test the starting income for UK tax gross-up
    def test_grossup_base(self):
        result = grossup_base(
            home="154545.45",
            deductions="36562.00",
            taxable="40545.45"
        )

        self.assertEqual(result, Decimal("158528.90"))
    
    # Test employer paid UK tax with hypothetical deductions and benefits
    def test_host_tax(self):
        result = host_tax(
            home="154545.45",
            deductions="36562.00",
            taxable="40545.45"
        )

        self.assertEqual(
            result["taxable_base"],
            Decimal("158528.90")
        )

        self.assertEqual(
            result["employer_tax"].quantize(Decimal("0.01")),
            Decimal("104620.01")
        )

        expected = uk_incometax(
            result["taxable_base"] + result["employer_tax"]
        )

        self.assertLess(
            abs(result["employer_tax"] - expected),
            Decimal("0.01")
        )
    
    # Test Swiss employer contributions converted into GBP
    def test_swiss_charges(self):
        result = swiss_charges("170000", "1.10")

        self.assertEqual(
            result["ahv"].quantize(Decimal("0.01")),
            Decimal("8190.91")
        )

        self.assertEqual(
            result["alv"].quantize(Decimal("0.01")),
            Decimal("1482.00")
        )

        self.assertEqual(
            result["total"].quantize(Decimal("0.01")),
            Decimal("9672.91")
        )

        self.assertEqual(
            result["total"],
            result["ahv"] + result["alv"]
        )
    
    # Test the complete employer cost calculation for Year 1
    def test_estimate_year(self):
        result = estimate_year(
            year=1,
            salary="150000",
            bonus="20000",
            rate="1.10",
            swiss_tax="29578",
            monthly_rent="3000",
            relocation="5000",
            moving="6000",
            temporary="4000",
            taxable_kind="36000"
        )

        self.assertEqual(
            result["pay"]["total"].quantize(Decimal("0.01")),
            Decimal("154545.45")
        )

        self.assertEqual(
            result["benefits"]["total"].quantize(Decimal("0.01")),
            Decimal("50545.45")
        )

        self.assertEqual(
            result["deductions"]["total"].quantize(Decimal("0.01")),
            Decimal("36562.00")
        )

        self.assertEqual(
            result["charges"]["total"].quantize(Decimal("0.01")),
            Decimal("9672.91")
        )

        self.assertEqual(
            result["taxable"]["total_taxable"].quantize(Decimal("0.01")),
            Decimal("50545.45")
        )

        tax = result["tax"]["employer_tax"]
        base = result["tax"]["taxable_base"]

        self.assertLess(
            abs(tax - uk_incometax(base + tax)),
            Decimal("0.01")
        )

        expected_cost = (
            result["pay"]["total"]
            + result["benefits"]["total"]
            + tax
            + result["charges"]["total"]
            - result["deductions"]["total"]
        )

        self.assertEqual(result["cost"]["total"], expected_cost)
    
    # Test employer cost calculation for the second year
    def test_estimate_year2(self):
        result = estimate_year(
            year=2,
            salary="150000",
            bonus="20000",
            rate="1.10",
            swiss_tax="29578",
            monthly_rent="3000",
            relocation="5000",
            moving="6000",
            temporary="4000",
            taxable_kind="36000"
        )

        self.assertEqual(
            result["pay"]["total"].quantize(Decimal("0.01")),
            Decimal("154545.45")
        )

        self.assertEqual(
            result["benefits"]["total"],
            Decimal("36000")
        )

        self.assertEqual(
            result["benefits"]["relocation"],
            Decimal("0")
        )

        self.assertEqual(
            result["benefits"]["moving"],
            Decimal("0")
        )

        self.assertEqual(
            result["benefits"]["temporary"],
            Decimal("0")
        )

        self.assertEqual(
            result["taxable"]["taxable_cash"],
            Decimal("0")
        )

        tax = result["tax"]["employer_tax"]
        base = result["tax"]["taxable_base"]

        self.assertLess(
            abs(tax - uk_incometax(base + tax)),
            Decimal("0.01")
        )

        expected_cost = (
            result["pay"]["total"]
            + result["benefits"]["total"]
            + tax
            + result["charges"]["total"]
            - result["deductions"]["total"]
        )

        self.assertEqual(result["cost"]["total"], expected_cost)
    
    # Test the complete two-year employer cost estimate
    def test_estimate_assignment(self):
        result = estimate_assignment(
            salary="150000",
            bonus="20000",
            rate="1.10",
            swiss_tax="29578",
            monthly_rent="3000",
            relocation="5000",
            moving="6000",
            temporary="4000",
            taxable_kind1="36000",
            taxable_kind2="36000"
        )

        year1 = result["year1"]
        year2 = result["year2"]
        summary = result["summary"]

        self.assertEqual(
            year1["benefits"]["total"].quantize(Decimal("0.01")),
            Decimal("50545.45")
        )

        self.assertEqual(
            year2["benefits"]["total"],
            Decimal("36000")
        )

        self.assertEqual(
            summary["year1"],
            year1["cost"]["total"]
        )

        self.assertEqual(
            summary["year2"],
            year2["cost"]["total"]
        )

        self.assertEqual(
            summary["total"],
            summary["year1"] + summary["year2"]
        )

        self.assertEqual(
            summary["home_pay"].quantize(Decimal("0.01")),
            Decimal("309090.91")
        )

        self.assertEqual(
            summary["multiple"],
            summary["total"] / summary["home_pay"]
        )

        self.assertGreater(
            summary["year1"],
            summary["year2"]
        )
    
    # Test relocation relief in the annual employer estimate
    def test_year_relief(self):
        result = estimate_year(
            year=1,
            salary="150000",
            bonus="20000",
            rate="1.10",
            swiss_tax="29578",
            monthly_rent="3000",
            relocation="5000",
            moving="6000",
            temporary="4000",
            taxable_kind="36000",
            moving_ok=True,
            temporary_ok=True
        )

        relief = result["relief"]

        self.assertEqual(relief["moving_exempt"], Decimal("6000"))
        self.assertEqual(relief["temporary_exempt"], Decimal("2000"))
        self.assertEqual(relief["total_exempt"], Decimal("8000"))
        self.assertEqual(relief["total_non_exempt"], Decimal("2000"))

        self.assertEqual(
            result["benefits"]["total"].quantize(Decimal("0.01")),
            Decimal("50545.45")
        )
    
    # Check qualifying relocation excess is included in taxable benefits
    def test_relocation_taxable(self):
        result = estimate_year(
            year=1,
            salary="150000",
            bonus="20000",
            rate="1.10",
            swiss_tax="29578",
            monthly_rent="3000",
            relocation="5000",
            moving="6000",
            temporary="4000",
            taxable_kind="36000",
            moving_ok=True,
            temporary_ok=True
        )

        self.assertEqual(
            result["relief"]["qualifying_excess"],
            Decimal("2000")
        )

        self.assertEqual(
            result["taxable"]["taxable_kind"],
            Decimal("38000")
        )

        self.assertEqual(
            result["taxable"]["total_taxable"].quantize(Decimal("0.01")),
            Decimal("42545.45")
        )

        self.assertEqual(
            result["benefits"]["total"].quantize(Decimal("0.01")),
            Decimal("50545.45")
        )
    
    # Check relocation reporting for both assignment years
    def test_year_reporting(self):
        for year in (1, 2):
            with self.subTest(year=year):
                result = estimate_year(
                    year=year,
                    salary="150000",
                    bonus="20000",
                    rate="1.10",
                    swiss_tax="29578",
                    monthly_rent="3000",
                    relocation="5000",
                    moving="6000",
                    temporary="4000",
                    taxable_kind="36000",
                    moving_ok=True,
                    temporary_ok=True,
                    payment="employer_direct"
                )

                reporting = result["reporting"]
                expected = Decimal("2000") if year == 1 else Decimal("0")

                self.assertEqual(reporting["paye_value"], Decimal("0"))
                self.assertEqual(reporting["p11d_value"], expected)
                self.assertEqual(reporting["uk_class1_base"], Decimal("0"))
                self.assertEqual(reporting["uk_class1a_base"], expected)
                self.assertEqual(
                    reporting["payment_method"], "employer_direct"
                )
    
    # Test taxable relocation reimbursements in the annual estimate
    def test_relocation_reimbursed(self):
        result = estimate_year(
            year=1,
            salary="150000",
            bonus="20000",
            rate="1.10",
            swiss_tax="29578",
            monthly_rent="3000",
            relocation="5000",
            moving="6000",
            temporary="4000",
            taxable_kind="36000",
            moving_ok=True,
            temporary_ok=False,
            payment="reimbursed"
        )

        self.assertEqual(
            result["reporting"]["taxable_cash"],
            Decimal("4000")
        )

        self.assertEqual(
            result["taxable"]["taxable_cash"].quantize(Decimal("0.01")),
            Decimal("8545.45")
        )

        self.assertEqual(
            result["taxable"]["taxable_kind"],
            Decimal("36000")
        )

        self.assertEqual(
            result["taxable"]["total_taxable"].quantize(Decimal("0.01")),
            Decimal("44545.45")
        )

        self.assertEqual(
            result["benefits"]["total"].quantize(Decimal("0.01")),
            Decimal("50545.45")
        )
    
    # Test relocation eligibility and payment settings across both years
    def test_assignment_relocation(self):
        result = estimate_assignment(
            salary="150000",
            bonus="20000",
            rate="1.10",
            swiss_tax="29578",
            monthly_rent="3000",
            relocation="5000",
            moving="6000",
            temporary="4000",
            taxable_kind1="36000",
            taxable_kind2="36000",
            moving_ok=True,
            temporary_ok=False,
            payment="reimbursed"
        )

        year1 = result["year1"]
        year2 = result["year2"]

        self.assertEqual(
            year1["relief"]["total_exempt"],
            Decimal("6000")
        )

        self.assertEqual(
            year1["reporting"]["taxable_cash"],
            Decimal("4000")
        )

        self.assertEqual(
            year1["reporting"]["payment_method"],
            "reimbursed"
        )

        self.assertEqual(
            year1["taxable"]["total_taxable"].quantize(Decimal("0.01")),
            Decimal("44545.45")
        )

        self.assertEqual(
            year2["reporting"]["total_taxable"],
            Decimal("0")
        )

        self.assertEqual(
            result["summary"]["total"],
            year1["cost"]["total"] + year2["cost"]["total"]
        )
    
    # Test social security coverage in the annual estimate
    def test_year_coverage(self):
        inputs = {
            "year": 1,
            "salary": "150000",
            "bonus": "20000",
            "rate": "1.10",
            "swiss_tax": "29578",
            "monthly_rent": "3000",
            "relocation": "5000",
            "moving": "6000",
            "temporary": "4000",
            "taxable_kind": "36000"
        }

        confirmed = estimate_year(**inputs, certificate=True)
        unverified = estimate_year(**inputs, certificate=False)

        self.assertEqual(
            confirmed["coverage"]["country"],
            "Switzerland"
        )

        self.assertFalse(confirmed["coverage"]["uk_ni"])

        self.assertIsNone(unverified["coverage"]["country"])
        self.assertIsNone(unverified["coverage"]["uk_ni"])

        self.assertEqual(
            unverified["coverage"]["status"],
            "Coverage requires verification"
        )

        
        self.assertEqual(
            confirmed["charges"]["total"],
            unverified["charges"]["total"]
        )

        self.assertTrue(confirmed["charges"]["coverage_confirmed"])
        self.assertFalse(unverified["charges"]["coverage_confirmed"])

        self.assertTrue(confirmed["charges"]["provisional"])
        self.assertTrue(unverified["charges"]["provisional"])

        self.assertIn("additional employer charges", confirmed["charges"]["note"])
        self.assertIn("UK NI unresolved", unverified["charges"]["note"])

    
    # Test social security coverage across both assignment years
    def test_assignment_coverage(self):
        inputs = {
            "salary": "150000",
            "bonus": "20000",
            "rate": "1.10",
            "swiss_tax": "29578",
            "monthly_rent": "3000",
            "relocation": "5000",
            "moving": "6000",
            "temporary": "4000",
            "taxable_kind1": "36000",
            "taxable_kind2": "36000"
        }

        confirmed = estimate_assignment(**inputs, certificate=True)
        unverified = estimate_assignment(**inputs, certificate=False)

        for year in ("year1", "year2"):
            self.assertEqual(
                confirmed[year]["coverage"]["country"],
                "Switzerland"
            )

            self.assertFalse(
                confirmed[year]["coverage"]["uk_ni"]
            )

            self.assertIsNone(
                unverified[year]["coverage"]["country"]
            )

            self.assertIsNone(
                unverified[year]["coverage"]["uk_ni"]
            )

            
            self.assertEqual(
                confirmed[year]["charges"]["total"],
                unverified[year]["charges"]["total"]
            )

            self.assertTrue(confirmed[year]["charges"]["coverage_confirmed"])
            self.assertFalse(unverified[year]["charges"]["coverage_confirmed"])

            self.assertTrue(confirmed[year]["charges"]["provisional"])
            self.assertTrue(unverified[year]["charges"]["provisional"])
    
    # Test provisional status in the two-year assignment summary
    def test_assignment_provisional(self):
        result = estimate_assignment(
            salary="150000",
            bonus="20000",
            rate="1.10",
            swiss_tax="29578",
            monthly_rent="3000",
            relocation="5000",
            moving="6000",
            temporary="4000",
            taxable_kind1="36000",
            taxable_kind2="36000",
            certificate=True
        )

        summary = result["summary"]

        self.assertTrue(summary["provisional"])

        self.assertIn(
            "employer contributions",
            summary["note"]
        )

        self.assertEqual(
            summary["total"],
            result["year1"]["cost"]["total"]
            + result["year2"]["cost"]["total"]
        )
    
    # Test UK National Insurance integration in the annual estimate
    def test_year_uk_ni(self):
        inputs = {
            "year": 1,
            "salary": "150000",
            "bonus": "20000",
            "rate": "1.10",
            "swiss_tax": "29578",
            "monthly_rent": "3000",
            "relocation": "5000",
            "moving": "6000",
            "temporary": "4000",
            "taxable_kind": "36000",
            "moving_ok": True,
            "temporary_ok": True
        }

        confirmed = estimate_year(**inputs, certificate=True)
        unverified = estimate_year(**inputs, certificate=False)

        self.assertEqual(
            confirmed["uk_ni"]["liability"],
            Decimal("0")
        )

        self.assertIsNone(
            confirmed["uk_ni"]["illustrative"]
        )

        self.assertIsNone(
            unverified["uk_ni"]["liability"]
        )

        illustrative = unverified["uk_ni"]["illustrative"]

        expected_class1 = (
            unverified["pay"]["total"]
            + unverified["benefits"]["relocation"]
            - Decimal("5000")
        ) * Decimal("0.15")

        self.assertEqual(
            illustrative["class1"],
            expected_class1
        )

        self.assertEqual(
            illustrative["class1a"],
            Decimal("5700.00")
        )

        self.assertEqual(
            illustrative["total"],
            expected_class1 + Decimal("5700.00")
        )

        self.assertEqual(
            confirmed["cost"]["total"],
            unverified["cost"]["total"]
        )
    
    # Test UK National Insurance across both assignment years
    def test_assignment_uk_ni(self):
        inputs = {
            "salary": "150000",
            "bonus": "20000",
            "rate": "1.10",
            "swiss_tax": "29578",
            "monthly_rent": "3000",
            "relocation": "5000",
            "moving": "6000",
            "temporary": "4000",
            "taxable_kind1": "36000",
            "taxable_kind2": "36000",
            "moving_ok": True,
            "temporary_ok": True
        }

        confirmed = estimate_assignment(**inputs, certificate=True)
        unverified = estimate_assignment(**inputs, certificate=False)

        for year in ("year1", "year2"):
            self.assertEqual(
                confirmed[year]["uk_ni"]["liability"],
                Decimal("0")
            )

            self.assertIsNone(
                unverified[year]["uk_ni"]["liability"]
            )

            self.assertIsNotNone(
                unverified[year]["uk_ni"]["illustrative"]
            )

        year1_ni = unverified["year1"]["uk_ni"]["illustrative"]
        year2_ni = unverified["year2"]["uk_ni"]["illustrative"]

        self.assertEqual(year1_ni["class1a"], Decimal("5700.00"))
        self.assertEqual(year2_ni["class1a"], Decimal("5400.00"))

        self.assertGreater(year1_ni["class1"], year2_ni["class1"])

        self.assertEqual(
            confirmed["summary"]["total"],
            unverified["summary"]["total"]
        )
