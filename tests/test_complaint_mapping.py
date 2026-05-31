from __future__ import annotations

import unittest

from app.complaint_mapping import (
    CHIEF_COMPLAINT_CODE_TO_ID,
    COMPLAINT_TO_PROCEDURE_GROUPS,
    MKIOSK_TO_COMPLAINTS,
    complaint_id_from_chief_complaint,
    complaints_from_mkiosk_flags,
    required_procedure_groups_for_complaint,
)
from app.procedure_groups import PROCEDURE_GROUPS


class ComplaintMappingTests(unittest.TestCase):
    def test_complaint_id_from_chief_complaint_maps_known_aliases(self) -> None:
        for alias, expected_id in CHIEF_COMPLAINT_CODE_TO_ID.items():
            with self.subTest(alias=alias):
                self.assertEqual(complaint_id_from_chief_complaint(alias), expected_id)
                self.assertEqual(
                    complaint_id_from_chief_complaint(f" {alias.upper()} "),
                    expected_id,
                )

    def test_complaint_id_from_chief_complaint_returns_none_for_unknown_or_empty(
        self,
    ) -> None:
        for value in ("", "   ", "unknown"):
            with self.subTest(value=value):
                self.assertIsNone(complaint_id_from_chief_complaint(value))

    def test_required_procedure_groups_for_complaint_returns_valid_group_ids(
        self,
    ) -> None:
        valid_group_ids = set(PROCEDURE_GROUPS)

        for complaint_id in COMPLAINT_TO_PROCEDURE_GROUPS:
            with self.subTest(complaint_id=complaint_id):
                groups = required_procedure_groups_for_complaint(complaint_id)
                self.assertEqual(set(groups) - valid_group_ids, set())

    def test_required_procedure_groups_for_complaint_returns_empty_for_unknown(
        self,
    ) -> None:
        self.assertEqual(required_procedure_groups_for_complaint(0), [])
        self.assertEqual(required_procedure_groups_for_complaint(999), [])

    def test_complaints_from_mkiosk_flags_accepts_y_values(self) -> None:
        for value in ("Y", "Y1", " y "):
            with self.subTest(value=value):
                self.assertEqual(
                    complaints_from_mkiosk_flags({"MKioskTy1": value}),
                    MKIOSK_TO_COMPLAINTS["MKioskTy1"],
                )

    def test_complaints_from_mkiosk_flags_ignores_n_empty_none_and_unknown_values(
        self,
    ) -> None:
        for value in ("N", "N1", "", "   ", None, "unknown"):
            with self.subTest(value=value):
                self.assertEqual(
                    complaints_from_mkiosk_flags({"MKioskTy1": value}),
                    set(),
                )

    def test_complaints_from_mkiosk_flags_ignores_unknown_enabled_key(self) -> None:
        self.assertEqual(complaints_from_mkiosk_flags({"MKioskTy999": "Y"}), set())


if __name__ == "__main__":
    unittest.main()
