from decimal import Decimal
from django.test import SimpleTestCase

from .services.eligibility import visa_checks


class VisaEligibilityTests(SimpleTestCase):

    # Create a scenario with confirmed eligibility inputs
    def verified(self, **changes):
        inputs = {
            "salary_chf": 150000,
            "rate": Decimal("1.10"),
            "overseas_months": 36,
            "occupation_code": "2131",
            "occupation_eligible": True,
            "going_rate_gbp": 42600,
            "sponsor_licensed": True,
            "sponsor_a_rated": True,
            "cos_valid": True,
            "corporate_link": True,
            "current_employee": True,
            "genuine_job": True,
            "isc_compliant": True,
        }

        inputs.update(changes)
        return visa_checks(**inputs)

    def test_assignment_case(self):
        result = visa_checks(150000, Decimal("1.10"), 36)

        self.assertEqual(
            result["salary_gbp"].quantize(Decimal("0.01")),
            Decimal("136363.64")
        )
        self.assertTrue(result["salary_met"])
        self.assertTrue(result["employment_met"])
        self.assertTrue(result["high_earner"])
        self.assertEqual(result["status"], "verification_required")
        self.assertIn("occupation", result["pending"])
        self.assertIn("going_rate", result["pending"])

    def test_complete_checks(self):
        result = self.verified()

        self.assertEqual(result["status"], "core_requirements_met")
        self.assertEqual(result["failed"], [])
        self.assertEqual(result["pending"], [])
        self.assertTrue(result["going_rate_met"])

    def test_minimum_salary(self):
        result = self.verified(
            salary_chf=52500,
            rate=1,
            overseas_months=12
        )

        self.assertTrue(result["salary_met"])
        self.assertFalse(result["high_earner"])
        self.assertEqual(result["status"], "core_requirements_met")

    def test_below_salary(self):
        result = self.verified(
            salary_chf=50000,
            rate=1
        )

        self.assertFalse(result["salary_met"])
        self.assertIn("salary", result["failed"])
        self.assertEqual(result["status"], "requirements_not_met")

    def test_short_employment(self):
        result = self.verified(
            salary_chf=60000,
            rate=1,
            overseas_months=11
        )

        self.assertFalse(result["employment_met"])
        self.assertIn("employment", result["failed"])

    def test_high_earner(self):
        result = self.verified(
            salary_chf=73900,
            rate=1,
            overseas_months=0
        )

        self.assertTrue(result["high_earner"])
        self.assertTrue(result["employment_met"])

    def test_going_rate(self):
        result = self.verified(
            salary_chf=60000,
            rate=1,
            going_rate_gbp=70000
        )

        self.assertTrue(result["salary_met"])
        self.assertFalse(result["going_rate_met"])
        self.assertIn("going_rate", result["failed"])

    def test_part_time(self):
        result = self.verified(
            salary_chf=60000,
            rate=1,
            weekly_hours=30,
            going_rate_gbp=75000
        )

        self.assertEqual(
            result["adjusted_rate"],
            Decimal("60000")
        )
        self.assertTrue(result["going_rate_met"])

    def test_long_hours(self):
        result = self.verified(
            salary_chf=60000,
            rate=1,
            weekly_hours=60,
            going_rate_gbp=30000
        )

        self.assertEqual(
            result["general_salary"],
            Decimal("48000")
        )
        self.assertFalse(result["salary_met"])
        self.assertEqual(
            result["adjusted_rate"],
            Decimal("48000")
        )
        self.assertTrue(result["going_rate_met"])

    def test_high_earner_hours(self):
        result = self.verified(
            salary_chf=90000,
            rate=1,
            weekly_hours=60,
            overseas_months=0
        )

        self.assertFalse(result["high_earner"])
        self.assertFalse(result["employment_met"])

    def test_reference_hours(self):
        result = self.verified(
            salary_chf=70000,
            rate=1,
            weekly_hours=40,
            going_rate_hours=40,
            going_rate_gbp=70000
        )

        self.assertEqual(
            result["adjusted_rate"],
            Decimal("70000")
        )
        self.assertTrue(result["going_rate_met"])

    def test_permitted_allowances(self):
        result = self.verified(
            salary_chf=50000,
            rate=1,
            allowed_allowance_chf=3000
        )

        self.assertEqual(
            result["eligible_salary"],
            Decimal("53000")
        )
        self.assertTrue(result["salary_met"])

    def test_housing_allowance_cap(self):
        result = self.verified(
            salary_chf=42000,
            rate=1,
            housing_allowance_chf=24000
        )

        self.assertEqual(
            result["housing_allowance_used"],
            Decimal("18000")
        )
        self.assertEqual(
            result["eligible_salary"],
            Decimal("60000")
        )

    def test_missing_occupation(self):
        result = self.verified(
            occupation_code=None,
            occupation_eligible=True
        )

        self.assertIsNone(result["conditions"]["occupation"])
        self.assertEqual(
            result["status"],
            "verification_required"
        )

    def test_invalid_sponsor(self):
        result = self.verified(
            sponsor_licensed=False
        )

        self.assertIn("sponsor", result["failed"])
        self.assertEqual(
            result["status"],
            "requirements_not_met"
        )

    def test_invalid_inputs(self):
        invalid = [
            {"salary_chf": "NaN"},
            {"salary_chf": "Infinity"},
            {"salary_chf": -1},
            {"rate": 0},
            {"rate": -1},
            {"overseas_months": -1},
            {"overseas_months": 2.5},
            {"weekly_hours": 0},
            {"going_rate_hours": 0},
            {"going_rate_gbp": 0},
            {"allowed_allowance_chf": -1},
            {"housing_allowance_chf": -1},
            {"occupation_code": "123"},
            {"occupation_code": "12345"},
            {"occupation_code": "ABCD"},
            {"sponsor_licensed": "yes"},
            {"cos_valid": 1},
        ]

        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.verified(**values)

