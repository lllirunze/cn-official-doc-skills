from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_repository", ROOT / "scripts" / "validate_repository.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RepositoryValidationTests(unittest.TestCase):
    def test_rule_catalog_is_complete_and_unique(self) -> None:
        VALIDATOR.validate_rule_catalog()

    def test_core_behavior_cases_cover_all_required_rules(self) -> None:
        rules = VALIDATOR.validate_rule_catalog()
        VALIDATOR.validate_behavior_coverage(rules)

    def test_all_four_sources_pass_the_human_review_gate(self) -> None:
        VALIDATOR.validate_source_gate()

    def test_plugin_contains_exactly_the_v01_skills(self) -> None:
        VALIDATOR.validate_plugin_package()

    def test_deterministic_rules_detect_fixture_errors(self) -> None:
        expected = [
            ("CASE-PUNCT-002", {"PUNCT-ANNEX-A09"}),
            ("CASE-FORMAT-002", {"FORMAT-DOC-NUMBER-001"}),
            ("CASE-NUMBER-003", {"NUMBER-DATE-001"}),
            (
                "CASE-NUMBER-004",
                {
                    "NUMBER-DECIMAL-001",
                    "NUMBER-RANGE-001",
                    "NUMBER-ARABIC-MEASURE-001",
                },
            ),
            ("CASE-ROUTING-003", {"ROUTING-UPWARD-001"}),
            ("CASE-FORMAT-001", {"FORMAT-SIGNER-001"}),
            (
                "CASE-FORMAT-005",
                {
                    "FORMAT-TITLE-LAYOUT-001",
                    "FORMAT-ADDRESSEE-LAYOUT-001",
                    "FORMAT-BODY-001",
                },
            ),
            (
                "CASE-FORMAT-006",
                {"FORMAT-ATTACHMENT-NOTE-001", "FORMAT-ATTACHMENT-001"},
            ),
            (
                "CASE-FORMAT-007",
                {"FORMAT-DATE-001", "FORMAT-PAGE-NUMBER-001"},
            ),
        ]
        cases = {case["id"]: case for case in VALIDATOR.load_behavior_cases()}
        for case_id, expected_rule_ids in expected:
            with self.subTest(case_id=case_id):
                self.assertEqual(
                    VALIDATOR.evaluate_deterministic_case(cases[case_id]),
                    expected_rule_ids,
                )

    def test_valid_paper_dimensions_do_not_trigger_a_deterministic_error(self) -> None:
        cases = {case["id"]: case for case in VALIDATOR.load_behavior_cases()}
        self.assertEqual(
            VALIDATOR.evaluate_deterministic_case(cases["CASE-FORMAT-003"]), set()
        )


if __name__ == "__main__":
    unittest.main()
