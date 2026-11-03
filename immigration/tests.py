from decimal import Decimal
from django.test import SimpleTestCase
from .services.eligibility import visa_checks
from .services.fees import visa_fees
from .services.documents import document_checks
from .services.visitor import visitor_checks
from .services.sponsorship import sponsor_checks
from .services.timeline import immigration_timeline
from .forms import ImmigrationForm
from .services.assessment import assess_immigration

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
    
    def test_licence_priority(self):
        result = self.quote(
            licence_status="new",
            licence_priority=True
        )

        self.assertEqual(result["licence_priority"], Decimal("750"))
        self.assertEqual(result["mandatory_employer"], Decimal("4847"))
        self.assertEqual(result["optional_fees"], Decimal("750"))
        self.assertEqual(result["employer_total"], Decimal("5597"))
        self.assertEqual(result["overall_total"], Decimal("9003.50"))

    def test_cos_priority(self):
        result = self.quote(
            extra_cos_needed=True,
            cos_priority=True
        )

        self.assertEqual(result["cos_priority"], Decimal("350"))
        self.assertEqual(result["mandatory_employer"], Decimal("3165"))
        self.assertEqual(result["optional_fees"], Decimal("350"))
        self.assertEqual(result["employer_total"], Decimal("3515"))
        self.assertEqual(result["overall_total"], Decimal("6921.50"))

    def test_both_sponsor_priorities(self):
        result = self.quote(
            licence_status="new",
            licence_priority=True,
            extra_cos_needed=True,
            cos_priority=True
        )

        self.assertEqual(result["optional_fees"], Decimal("1100"))
        self.assertEqual(result["employer_total"], Decimal("5947"))
        self.assertEqual(
            result["employer_total"] + result["employee_total"],
            result["overall_total"]
        )

    def test_invalid_sponsor_priority(self):
        invalid = [
            {"licence_priority": True},
            {"cos_priority": True},
            {"licence_priority": "yes"},
            {"cos_priority": 1},
            {"extra_cos_needed": None},
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

class VisitorRequirementTests(SimpleTestCase):

    # Build the standard pre-assignment business visit
    def visit(self, **changes):
        inputs = {
            "purpose": "meetings",
            "visit_months": 1,
            "passport_valid": True,
            "eta_exemption": "none",
            "has_valid_eta": False,
        }
        inputs.update(changes)
        return visitor_checks(**inputs)

    def test_standard_business_visit(self):
        result = self.visit()

        self.assertEqual(
            result["status"],
            "visitor_activity_permitted"
        )
        self.assertEqual(
            result["visa_status"],
            "visitor_visa_not_required"
        )
        self.assertTrue(result["eta_required"])
        self.assertTrue(result["eta_application_needed"])
        self.assertEqual(result["eta_cost"], Decimal("20"))

    def test_permitted_activities(self):
        activities = [
            "meetings",
            "conferences",
            "negotiations",
            "site_visit",
        ]

        for purpose in activities:
            with self.subTest(purpose=purpose):
                result = self.visit(purpose=purpose)
                self.assertEqual(
                    result["status"],
                    "visitor_activity_permitted"
                )

    def test_existing_eta(self):
        result = self.visit(has_valid_eta=True)

        self.assertTrue(result["eta_required"])
        self.assertFalse(result["eta_application_needed"])
        self.assertEqual(result["eta_cost"], Decimal("0"))

    def test_eta_exemptions(self):
        exemptions = [
            "uk_permission",
            "british_irish",
            "ireland_resident_cta",
        ]

        for exemption in exemptions:
            with self.subTest(exemption=exemption):
                result = self.visit(eta_exemption=exemption)

                self.assertFalse(result["eta_required"])
                self.assertFalse(result["eta_application_needed"])
                self.assertEqual(result["eta_cost"], Decimal("0"))

    def test_invalid_passport(self):
        result = self.visit(passport_valid=False)

        self.assertEqual(result["status"], "passport_invalid")
        self.assertIsNone(result["eta_required"])
        self.assertEqual(result["eta_cost"], Decimal("0"))

    def test_visit_duration(self):
        allowed = self.visit(visit_months=6)
        excessive = self.visit(visit_months=Decimal("6.1"))

        self.assertEqual(
            allowed["status"],
            "visitor_activity_permitted"
        )
        self.assertEqual(
            excessive["status"],
            "visit_too_long"
        )
        self.assertEqual(
            excessive["visa_status"],
            "requirements_not_met"
        )

    def test_uk_employment(self):
        result = self.visit(purpose="uk_employment")

        self.assertEqual(
            result["status"],
            "work_visa_required"
        )
        self.assertEqual(
            result["visa_status"],
            "work_visa_required"
        )
        self.assertIsNone(result["eta_application_needed"])

    def test_activities_requiring_review(self):
        for purpose in ("training", "other"):
            with self.subTest(purpose=purpose):
                result = self.visit(purpose=purpose)

                self.assertEqual(
                    result["status"],
                    "activity_verification_required"
                )
                self.assertEqual(
                    result["visa_status"],
                    "verification_required"
                )

    def test_eta_information(self):
        result = self.visit()

        self.assertEqual(
            result["eta_validity_months"],
            Decimal("24")
        )
        self.assertEqual(
            result["max_visit_months"],
            Decimal("6")
        )
        self.assertIn("three working days", result["eta_processing"])

    def test_sources_and_warnings(self):
        result = self.visit()

        for url in result["sources"].values():
            self.assertTrue(url.startswith("https://"))

        self.assertTrue(result["warnings"])
        self.assertTrue(
            any("work visa" in warning for warning in result["warnings"])
        )

    def test_invalid_inputs(self):
        invalid = [
            {"visit_months": 0},
            {"visit_months": -1},
            {"visit_months": "NaN"},
            {"visit_months": "Infinity"},
            {"visit_months": "invalid"},
            {"purpose": "holiday_work"},
            {"eta_exemption": "unknown"},
            {"passport_valid": None},
            {"passport_valid": "yes"},
            {"has_valid_eta": 1},
            {"has_valid_eta": None},
        ]

        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.visit(**values)

class SponsorshipTests(SimpleTestCase):

    # Create an employer with confirmed sponsorship requirements
    def verified(self, **changes):
        inputs = {
            "licence_valid": True,
            "route_authorised": True,
            "rating": "A",
            "continuing_same_route": False,
            "link_type": "common_control",
            "link_verified": True,
            "linked_entity_recorded": True,
            "genuine_job": True,
            "lawful_job": True,
            "cos_available": True,
            "cos_assigned": True,
            "cos_valid": True,
            "isc_paid": True,
            "isc_exempt": False,
        }

        inputs.update(changes)
        return sponsor_checks(**inputs)

    def test_default_assessment(self):
        result = sponsor_checks()

        self.assertEqual(
            result["status"],
            "verification_required"
        )
        self.assertEqual(len(result["checks"]), 10)
        self.assertEqual(len(result["pending"]), 10)
        self.assertEqual(result["actions"], [])

    def test_complete_sponsorship(self):
        result = self.verified()

        self.assertEqual(
            result["status"],
            "sponsorship_requirements_met"
        )
        self.assertEqual(result["pending"], [])
        self.assertEqual(result["actions"], [])
        self.assertEqual(result["cos_type"], "undefined")

        for item in result["checks"]:
            self.assertEqual(item["status"], "met")

    def test_licence_and_route(self):
        cases = [
            ({"licence_valid": False}, "licence"),
            ({"route_authorised": False}, "route"),
        ]

        for changes, expected in cases:
            with self.subTest(changes=changes):
                result = self.verified(**changes)

                self.assertIn(expected, result["actions"])
                self.assertEqual(
                    result["status"],
                    "action_required"
                )

    def test_b_rated_sponsor(self):
        continuing = self.verified(
            rating="B",
            continuing_same_route=True
        )
        new_assignment = self.verified(
            rating="B",
            continuing_same_route=False
        )

        self.assertEqual(
            continuing["status"],
            "sponsorship_requirements_met"
        )
        self.assertIn("rating", new_assignment["actions"])

    def test_unacceptable_rating(self):
        for rating in ("provisional", "none"):
            with self.subTest(rating=rating):
                result = self.verified(rating=rating)

                self.assertIn("rating", result["actions"])

    def test_corporate_relationship(self):
        missing = self.verified(link_type="no_link")
        unknown = self.verified(link_type="unknown")
        unverified = self.verified(link_verified=None)
        confirmed = self.verified(
            link_type="joint_venture",
            link_verified=True
        )

        self.assertIn("corporate_link", missing["actions"])
        self.assertIn("corporate_link", unknown["pending"])
        self.assertIn("corporate_link", unverified["pending"])
        self.assertEqual(
            confirmed["status"],
            "sponsorship_requirements_met"
        )

    def test_cos_requirements(self):
        no_allocation = self.verified(cos_available=False)
        not_assigned = self.verified(
            cos_assigned=False,
            cos_valid=False
        )
        unverified = self.verified(cos_valid=None)

        self.assertIn("allocation", no_allocation["actions"])
        self.assertIn("certificate", not_assigned["actions"])
        self.assertIn("certificate", unverified["pending"])

    def test_isc_requirements(self):
        unpaid = self.verified(isc_paid=False)
        exempt = self.verified(
            isc_paid=False,
            isc_exempt=True
        )

        self.assertIn("isc", unpaid["actions"])
        self.assertEqual(
            exempt["status"],
            "sponsorship_requirements_met"
        )

    def test_incomplete_information(self):
        result = self.verified(
            licence_valid=None,
            linked_entity_recorded=None
        )

        self.assertEqual(
            result["status"],
            "verification_required"
        )
        self.assertIn("licence", result["pending"])
        self.assertIn("linked_entity", result["pending"])

    def test_multiple_failures(self):
        result = self.verified(
            licence_valid=False,
            route_authorised=False,
            genuine_job=False,
            isc_paid=False
        )

        self.assertEqual(result["status"], "action_required")
        self.assertEqual(len(result["actions"]), 4)

    def test_employer_duties_and_sources(self):
        result = self.verified()

        self.assertEqual(len(result["duties"]), 6)
        self.assertEqual(
            result["cos_rules"]["apply_within_months"],
            3
        )
        self.assertEqual(
            result["cos_rules"]["earliest_application_months"],
            3
        )

        for item in result["checks"] + result["duties"]:
            self.assertTrue(item["source"].startswith("https://"))
            self.assertTrue(item["title"])

        self.assertTrue(result["notes"])

    def test_invalid_inputs(self):
        invalid = [
            {"licence_valid": "yes"},
            {"route_authorised": 1},
            {"rating": "gold"},
            {"continuing_same_route": None},
            {"link_type": "ownership"},
            {"link_verified": 0},
            {"linked_entity_recorded": "yes"},
            {"genuine_job": "true"},
            {"cos_available": 1},
            {"isc_paid": "paid"},
            {"isc_exempt": "yes"},
        ]

        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.verified(**values)

    def test_inconsistent_cos_inputs(self):
        invalid = [
            {"cos_assigned": False, "cos_valid": True},
            {"cos_assigned": None, "cos_valid": True},
        ]

        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.verified(**values)

class ImmigrationTimelineTests(SimpleTestCase):

    # Build the standard immigration timeline
    def timeline(self, **changes):
        inputs = {
            "licence_status": "existing",
            "licence_priority": False,
            "extra_cos_needed": False,
            "cos_priority": False,
            "location": "outside",
            "priority": "none",
            "eta_needed": False,
        }

        inputs.update(changes)
        return immigration_timeline(**inputs)

    def test_default_timeline(self):
        result = self.timeline()

        self.assertEqual(result["route"], "Senior or Specialist Worker")
        self.assertEqual(len(result["work_stages"]), 2)
        self.assertEqual(result["work_stages"][0]["code"], "certificate")
        self.assertEqual(result["work_stages"][1]["code"], "visa")
        self.assertEqual(
            result["work_stages"][1]["time"],
            "Usually within 3 weeks"
        )
        self.assertEqual(result["visitor_stages"], [])
        self.assertIsNone(result["total_time"])

    def test_new_sponsor_licence(self):
        result = self.timeline(licence_status="new")

        self.assertEqual(len(result["work_stages"]), 3)
        self.assertEqual(result["work_stages"][0]["code"], "licence")
        self.assertIn(
            "8 weeks",
            result["work_stages"][0]["time"]
        )

    def test_priority_licence(self):
        result = self.timeline(
            licence_status="new",
            licence_priority=True
        )

        self.assertEqual(
            result["work_stages"][0]["time"],
            "Within 10 working days"
        )

    def test_route_addition(self):
        result = self.timeline(licence_status="add_worker")

        self.assertEqual(result["work_stages"][0]["code"], "licence")
        self.assertEqual(
            result["work_stages"][0]["time"],
            "Processing time requires verification"
        )

    def test_cos_allocation(self):
        result = self.timeline(extra_cos_needed=True)

        codes = [item["code"] for item in result["work_stages"]]

        self.assertEqual(
            codes,
            ["allocation", "certificate", "visa"]
        )
        self.assertEqual(
            result["work_stages"][0]["time"],
            "Usually within 12 weeks"
        )

    def test_priority_cos(self):
        result = self.timeline(
            extra_cos_needed=True,
            cos_priority=True
        )

        self.assertEqual(
            result["work_stages"][0]["time"],
            "Within 5 working days"
        )

    def test_application_location(self):
        outside = self.timeline(location="outside")
        inside = self.timeline(location="inside")

        self.assertEqual(
            outside["work_stages"][-1]["time"],
            "Usually within 3 weeks"
        )
        self.assertEqual(
            inside["work_stages"][-1]["time"],
            "Usually within 8 weeks"
        )

    def test_visa_priority(self):
        priority = self.timeline(priority="priority")
        super_priority = self.timeline(priority="super")

        self.assertEqual(
            priority["work_stages"][-1]["time"],
            "Usually within 5 working days"
        )
        self.assertEqual(
            super_priority["work_stages"][-1]["time"],
            "Usually by the next working day"
        )

    def test_eta_separate(self):
        result = self.timeline(eta_needed=True)

        self.assertEqual(len(result["work_stages"]), 2)
        self.assertEqual(len(result["visitor_stages"]), 1)
        self.assertEqual(
            result["visitor_stages"][0]["code"],
            "eta"
        )
        self.assertIn(
            "3 working days",
            result["visitor_stages"][0]["time"]
        )

    def test_application_rules(self):
        result = self.timeline()

        self.assertEqual(
            result["application_rules"]["cos_valid_months"],
            3
        )
        self.assertEqual(
            result["application_rules"]["earliest_apply_months"],
            3
        )
        self.assertIsNone(result["total_time"])

    def test_sources_and_notes(self):
        result = self.timeline(
            licence_status="new",
            extra_cos_needed=True,
            eta_needed=True
        )

        stages = (
            result["work_stages"] +
            result["visitor_stages"]
        )

        for stage in stages:
            self.assertTrue(stage["source"].startswith("https://"))
            self.assertTrue(stage["title"])
            self.assertTrue(stage["time"])
            self.assertTrue(stage["note"])

        self.assertTrue(result["notes"])
        self.assertTrue(result["total_status"])

    def test_invalid_inputs(self):
        invalid = [
            {"licence_status": "invalid"},
            {"licence_status": None},
            {"location": "unknown"},
            {"location": None},
            {"priority": "fast"},
            {"priority": None},
            {"licence_priority": "yes"},
            {"licence_priority": None},
            {"extra_cos_needed": 1},
            {"extra_cos_needed": None},
            {"cos_priority": "true"},
            {"cos_priority": None},
            {"eta_needed": 1},
            {"eta_needed": None},
        ]

        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.timeline(**values)

    def test_inconsistent_options(self):
        invalid = [
            {"licence_priority": True},
            {"licence_status": "add_worker", "licence_priority": True},
            {"cos_priority": True},
        ]

        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    self.timeline(**values)

    def test_priority_fee_consistency(self):
        timeline = self.timeline(
            licence_status="new",
            licence_priority=True,
            extra_cos_needed=True,
            cos_priority=True
        )

        fees = visa_fees(
            assignment_months=24,
            permission_months=Decimal("24.5"),
            licence_status="new",
            licence_priority=True,
            extra_cos_needed=True,
            cos_priority=True
        )

        self.assertEqual(
            timeline["work_stages"][0]["time"],
            "Within 10 working days"
        )
        self.assertEqual(
            timeline["work_stages"][1]["time"],
            "Within 5 working days"
        )
        self.assertEqual(fees["licence_priority"], Decimal("750"))
        self.assertEqual(fees["cos_priority"], Decimal("350"))
        self.assertEqual(fees["optional_fees"], Decimal("1100"))

class ImmigrationAssessmentTests(SimpleTestCase):

    # Build form inputs using the configured defaults
    def inputs(self, **changes):
        values = {
            name: field.initial
            for name, field in ImmigrationForm.base_fields.items()
            if field.initial is not None
        }
        values.update(changes)
        return values

    # Validate the form before running the assessment
    def assess(self, **changes):
        form = ImmigrationForm(data=self.inputs(**changes))
        self.assertTrue(form.is_valid(), form.errors.as_text())
        return assess_immigration(form.cleaned_data)

    def test_default_assignment(self):
        result = self.assess()

        self.assertEqual(result["status"], "verification_required")
        self.assertTrue(result["eligibility"]["salary_met"])
        self.assertTrue(result["eligibility"]["employment_met"])
        self.assertEqual(
            result["sponsorship"]["status"],
            "verification_required"
        )
        self.assertEqual(result["fees"]["eta"], Decimal("20"))
        self.assertEqual(
            result["fees"]["overall_total"],
            Decimal("6591.50")
        )
        self.assertEqual(
            result["documents"]["maintenance_amount"],
            Decimal("1270")
        )
        self.assertEqual(len(result["timeline"]["visitor_stages"]), 1)

    def test_no_business_visit(self):
        result = self.assess(plan_visit=False)

        self.assertIsNone(result["visitor"])
        self.assertEqual(result["fees"]["eta"], Decimal("0"))
        self.assertEqual(result["timeline"]["visitor_stages"], [])
        self.assertEqual(
            result["fees"]["overall_total"],
            Decimal("6571.50")
        )

    def test_existing_eta(self):
        result = self.assess(has_valid_eta=True)

        self.assertTrue(result["visitor"]["eta_required"])
        self.assertFalse(result["visitor"]["eta_application_needed"])
        self.assertEqual(result["fees"]["eta"], Decimal("0"))
        self.assertEqual(result["timeline"]["visitor_stages"], [])

    def test_complete_core_requirements(self):
        result = self.assess(
            occupation_code="2131",
            occupation_eligible="yes",
            going_rate_gbp=42600,
            licence_valid="yes",
            route_authorised="yes",
            rating="A",
            link_type="common_control",
            link_verified="yes",
            linked_entity_recorded="yes",
            genuine_job="yes",
            lawful_job="yes",
            cos_available="yes",
            cos_assigned="yes",
            cos_valid="yes",
            isc_paid="yes",
        )

        self.assertEqual(result["status"], "core_requirements_met")
        self.assertEqual(result["eligibility"]["failed"], [])
        self.assertEqual(result["eligibility"]["pending"], [])
        self.assertEqual(result["sponsorship"]["actions"], [])
        self.assertEqual(result["sponsorship"]["pending"], [])

    def test_sponsor_not_licensed(self):
        result = self.assess(licence_valid="no")

        self.assertEqual(
            result["sponsorship"]["status"],
            "action_required"
        )
        self.assertIn("licence", result["sponsorship"]["actions"])
        self.assertEqual(result["status"], "requirements_not_met")

    def test_sponsor_priority_integration(self):
        result = self.assess(
            licence_status="new",
            licence_priority=True,
            extra_cos_needed=True,
            cos_priority=True,
        )

        fees = result["fees"]
        stages = result["timeline"]["work_stages"]

        self.assertEqual(fees["licence_priority"], Decimal("750"))
        self.assertEqual(fees["cos_priority"], Decimal("350"))
        self.assertEqual(
            fees["mandatory_employer"],
            Decimal("4847")
        )
        self.assertEqual(
            fees["overall_total"],
            Decimal("9373.50")
        )
        self.assertEqual(
            stages[0]["time"],
            "Within 10 working days"
        )
        self.assertEqual(
            stages[1]["time"],
            "Within 5 working days"
        )

    def test_visitor_employment_restriction(self):
        result = self.assess(purpose="uk_employment")

        self.assertEqual(
            result["visitor"]["status"],
            "work_visa_required"
        )
        self.assertEqual(result["fees"]["eta"], Decimal("0"))
        self.assertEqual(result["timeline"]["visitor_stages"], [])

    def test_maintenance_integration(self):
        result = self.assess(sponsor_maintenance=True)

        self.assertEqual(
            result["documents"]["maintenance_amount"],
            Decimal("0")
        )
        self.assertEqual(
            result["fees"]["maintenance_evidence"],
            Decimal("0")
        )

    def test_employer_funded_fees(self):
        result = self.assess(
            employer_pays_visa=True,
            employer_pays_ihs=True,
            employer_pays_eta=True,
        )

        self.assertEqual(
            result["fees"]["employer_total"],
            Decimal("6591.50")
        )
        self.assertEqual(
            result["fees"]["employee_total"],
            Decimal("0")
        )

    def test_form_validation(self):
        cases = [
            {"permission_months": Decimal("12")},
            {"licence_priority": True},
            {"cos_priority": True},
            {"cos_valid": "yes", "cos_assigned": "no"},
        ]

        for changes in cases:
            with self.subTest(changes=changes):
                form = ImmigrationForm(data=self.inputs(**changes))
                self.assertFalse(form.is_valid())
