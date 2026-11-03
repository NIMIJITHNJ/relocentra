from decimal import Decimal
from django.test import SimpleTestCase
from .services.eligibility import visa_checks
from .services.fees import visa_fees
from .services.documents import document_checks


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

class ImmigrationFeeTests(SimpleTestCase):

    # Build the standard two-year assignment scenario
    def quote(self, **changes):
        inputs = {
            "assignment_months": 24,
            "permission_months": Decimal("24.5"),
        }
        inputs.update(changes)
        return visa_fees(**inputs)

    def test_assignment_costs(self):
        result = self.quote()

        self.assertEqual(result["visa"], Decimal("819"))
        self.assertEqual(result["ihs"], Decimal("2587.50"))
        self.assertEqual(result["cos"], Decimal("525"))
        self.assertEqual(result["isc"], Decimal("2640"))
        self.assertEqual(result["licence"], Decimal("0"))
        self.assertEqual(result["mandatory_employer"], Decimal("3165"))
        self.assertEqual(result["overall_total"], Decimal("6571.50"))
        self.assertEqual(result["employer_total"], Decimal("3165"))
        self.assertEqual(result["employee_total"], Decimal("3406.50"))
        self.assertEqual(result["ihs_blocks"], Decimal("5"))

    def test_small_sponsor(self):
        result = self.quote(sponsor_size="small")

        self.assertEqual(result["isc"], Decimal("960"))
        self.assertEqual(result["mandatory_employer"], Decimal("1485"))
        self.assertEqual(result["overall_total"], Decimal("4891.50"))

    def test_new_licence(self):
        large = self.quote(licence_status="new")
        small = self.quote(
            sponsor_size="small",
            licence_status="new"
        )

        self.assertEqual(large["licence"], Decimal("1682"))
        self.assertEqual(small["licence"], Decimal("611"))
        self.assertEqual(large["employer_total"], Decimal("4847"))
        self.assertEqual(small["employer_total"], Decimal("2096"))

    def test_add_worker_licence(self):
        large = self.quote(licence_status="add_worker")
        small = self.quote(
            sponsor_size="small",
            licence_status="add_worker"
        )

        self.assertEqual(large["licence"], Decimal("1071"))
        self.assertEqual(small["licence"], Decimal("0"))

    def test_isc_exemption(self):
        result = self.quote(isc_exempt=True)

        self.assertEqual(result["isc"], Decimal("0"))
        self.assertEqual(result["mandatory_employer"], Decimal("525"))

    def test_isc_duration(self):
        cases = [
            (6, 1320),
            (7, 1320),
            (12, 1320),
            (13, 1980),
            (18, 1980),
            (19, 2640),
            (24, 2640),
            (25, 3300),
            (60, 6600),
        ]

        for months, expected in cases:
            with self.subTest(months=months):
                result = self.quote(
                    assignment_months=months,
                    permission_months=months
                )
                self.assertEqual(
                    result["isc"],
                    Decimal(str(expected))
                )

    def test_ihs_duration(self):
        cases = [
            ("6", "0"),
            ("6.1", "1035"),
            ("12", "1035"),
            ("12.1", "1552.50"),
            ("18", "1552.50"),
            ("18.1", "2070"),
            ("24", "2070"),
            ("24.1", "2587.50"),
            ("30", "2587.50"),
        ]

        for months, expected in cases:
            with self.subTest(months=months):
                result = self.quote(
                    assignment_months=1,
                    permission_months=Decimal(months)
                )
                self.assertEqual(
                    result["ihs"],
                    Decimal(expected)
                )

    def test_short_visa_outside(self):
        result = self.quote(
            assignment_months=5,
            permission_months=5
        )

        self.assertEqual(result["ihs"], Decimal("0"))
        self.assertEqual(result["isc"], Decimal("0"))
        self.assertEqual(result["overall_total"], Decimal("1344"))

    def test_short_visa_inside(self):
        result = self.quote(
            assignment_months=5,
            permission_months=5,
            location="inside"
        )

        self.assertEqual(result["visa"], Decimal("943"))
        self.assertEqual(result["ihs"], Decimal("517.50"))
        self.assertEqual(result["isc"], Decimal("1320"))
        self.assertEqual(result["overall_total"], Decimal("3305.50"))

    def test_visa_fee_threshold(self):
        cases = [
            ("outside", "36", "819"),
            ("outside", "36.1", "1618"),
            ("inside", "36", "943"),
            ("inside", "36.1", "1865"),
        ]

        for location, months, expected in cases:
            with self.subTest(location=location, months=months):
                result = self.quote(
                    location=location,
                    assignment_months=24,
                    permission_months=Decimal(months)
                )
                self.assertEqual(result["visa"], Decimal(expected))

    def test_employer_pays_all(self):
        result = self.quote(
            employer_pays_visa=True,
            employer_pays_ihs=True
        )

        self.assertEqual(
            result["employer_total"],
            Decimal("6571.50")
        )
        self.assertEqual(result["employee_total"], Decimal("0"))

    def test_optional_services(self):
        result = self.quote(
            priority="priority",
            eta=True,
            employer_pays_priority=True,
            employer_pays_eta=True
        )

        self.assertEqual(result["priority"], Decimal("500"))
        self.assertEqual(result["eta"], Decimal("20"))
        self.assertEqual(result["optional_fees"], Decimal("520"))
        self.assertEqual(result["overall_total"], Decimal("7091.50"))
        self.assertEqual(result["employer_total"], Decimal("3685"))

    def test_super_priority(self):
        result = self.quote(priority="super")

        self.assertEqual(result["priority"], Decimal("1000"))
        self.assertEqual(result["optional_fees"], Decimal("1000"))

    def test_maintenance(self):
        normal = self.quote()
        certified = self.quote(maintenance_certified=True)

        self.assertEqual(
            normal["maintenance_evidence"],
            Decimal("1270")
        )
        self.assertEqual(
            certified["maintenance_evidence"],
            Decimal("0")
        )
        self.assertEqual(
            normal["overall_total"],
            certified["overall_total"]
        )

    def test_cost_balance(self):
        result = self.quote(
            sponsor_size="small",
            licence_status="new",
            eta=True,
            priority="priority",
            employer_pays_visa=True,
            employer_pays_eta=True
        )

        self.assertEqual(
            result["employer_total"] + result["employee_total"],
            result["overall_total"]
        )

    def test_invalid_inputs(self):
        invalid = [
            {"assignment_months": 0},
            {"assignment_months": -1},
            {"assignment_months": 61},
            {"assignment_months": 2.5},
            {"assignment_months": "NaN"},
            {"permission_months": 0},
            {"permission_months": "Infinity"},
            {"permission_months": -1},
            {"permission_months": 12},
            {"sponsor_size": "medium"},
            {"location": "unknown"},
            {"licence_status": "invalid"},
            {"priority": "fast"},
            {"isc_exempt": "yes"},
            {"eta": 1},
            {"employer_pays_visa": "true"},
            {"maintenance_certified": None},
        ]

        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.quote(**values)

class DocumentRequirementTests(SimpleTestCase):

    # Build the standard Swiss-to-UK assignment scenario
    def checklist(self, **changes):
        inputs = {
            "eligible_salary_gbp": Decimal("136363.64"),
            "uk_months": 0,
        }
        inputs.update(changes)
        return document_checks(**inputs)

    def test_assignment_documents(self):
        result = self.checklist()

        self.assertEqual(len(result["items"]), 12)
        self.assertEqual(
            result["maintenance_amount"],
            Decimal("1270")
        )

        for code in ("passport", "cos", "employment", "sponsor", "funds"):
            self.assertIn(code, result["required"])

    def test_sponsor_maintenance(self):
        result = self.checklist(sponsor_maintenance=True)

        self.assertEqual(
            result["maintenance_amount"],
            Decimal("0")
        )
        self.assertNotIn("funds", result["required"])

    def test_existing_uk_residence(self):
        result = self.checklist(uk_months=12)

        self.assertEqual(
            result["maintenance_amount"],
            Decimal("0")
        )
        self.assertNotIn("funds", result["required"])

    def test_overseas_employment_evidence(self):
        regular = self.checklist(eligible_salary_gbp=73900)
        lower = self.checklist(eligible_salary_gbp=73899)

        items_regular = {
            item["code"]: item for item in regular["items"]
        }
        items_lower = {
            item["code"]: item for item in lower["items"]
        }

        self.assertEqual(
            items_regular["overseas"]["status"],
            "not_required"
        )
        self.assertEqual(
            items_lower["overseas"]["status"],
            "may_be_requested"
        )

    def test_conditional_documents_required(self):
        result = self.checklist(
            tb_required=True,
            atas_required=True,
            translations_required=True,
            scholarship_consent=True,
            dependants=True
        )

        for code in (
            "tb", "atas", "translations",
            "scholarship", "dependants"
        ):
            self.assertIn(code, result["required"])

    def test_conditional_documents_not_required(self):
        result = self.checklist(
            tb_required=False,
            atas_required=False,
            translations_required=False,
            scholarship_consent=False,
            dependants=False
        )

        for code in (
            "tb", "atas", "translations",
            "scholarship", "dependants"
        ):
            self.assertNotIn(code, result["required"])
            self.assertNotIn(code, result["to_verify"])

    def test_unverified_requirements(self):
        result = self.checklist()

        for code in (
            "tb", "atas", "translations",
            "scholarship", "identity"
        ):
            self.assertIn(code, result["to_verify"])

    def test_document_sources(self):
        result = self.checklist()

        for item in result["items"]:
            self.assertTrue(item["source"].startswith("https://"))
            self.assertTrue(item["title"])
            self.assertTrue(item["details"])

    def test_unique_document_codes(self):
        result = self.checklist()

        codes = [item["code"] for item in result["items"]]
        self.assertEqual(len(codes), len(set(codes)))

    def test_invalid_inputs(self):
        invalid = [
            {"eligible_salary_gbp": -1},
            {"eligible_salary_gbp": "NaN"},
            {"eligible_salary_gbp": "Infinity"},
            {"eligible_salary_gbp": "invalid"},
            {"uk_months": -1},
            {"uk_months": 2.5},
            {"uk_months": "NaN"},
            {"sponsor_maintenance": None},
            {"sponsor_maintenance": "yes"},
            {"tb_required": "yes"},
            {"atas_required": 1},
            {"dependants": None},
            {"translations_required": "unknown"},
            {"scholarship_consent": 1},
        ]

        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.checklist(**values)
