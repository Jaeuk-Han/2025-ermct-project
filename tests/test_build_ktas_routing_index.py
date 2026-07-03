from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.build_ktas_routing_index import (
    build_index,
    load_aliases,
    load_feature_hints,
    parse_rows,
)


class ParseRowsTests(unittest.TestCase):
    @staticmethod
    def write_csv(directory: str, content: str) -> Path:
        path = Path(directory) / "input.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def test_parses_quoted_comma_and_integer_ktas(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.write_csv(
                directory,
                'COFAA,O,환경손상,F,저체온증,AA,"중증, 호흡곤란",1\n',
            )
            rows, warnings = parse_rows(path)

        self.assertEqual([], warnings)
        self.assertEqual("중증, 호흡곤란", rows[0]["detail_label"])
        self.assertEqual(1, rows[0]["ktas"])

    def test_skips_invalid_rows_and_warns_for_both_duplicate_keys(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.write_csv(
                directory,
                "0,1,2,3,4,5,6,7\n"
                "COFAA,O,환경손상,F,저체온증,AA,중증 호흡곤란,1\n"
                "COFAA,O,환경손상,F,저체온증,AA,다른 문구,4\n"
                "BAD,O,환경손상,F,저체온증,AC,기준,not-int\n"
                ",O,환경손상,F,저체온증,AD,기준,2\n",
            )
            rows, warnings = parse_rows(path)

        self.assertEqual(["COFAA"], [row["row_code"] for row in rows])
        self.assertTrue(
            any("duplicate row_code=COFAA" in warning for warning in warnings)
        )
        self.assertTrue(
            any("duplicate detail_key=O:F:AA" in warning for warning in warnings)
        )
        self.assertTrue(any("invalid ktas" in warning for warning in warnings))
        self.assertTrue(
            any("missing required fields" in warning for warning in warnings)
        )


class BuildIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            {
                "row_code": "COFAA",
                "category_code": "O",
                "category_label": "환경손상",
                "complaint_code": "F",
                "complaint_label": " 저체온증 ",
                "detail_code": "AA",
                "detail_label": " 중증 호흡곤란 ",
                "ktas": 1,
            },
            {
                "row_code": "CPFAA",
                "category_code": "P",
                "category_label": "일반",
                "complaint_code": "F",
                "complaint_label": "저체온증",
                "detail_code": "AA",
                "detail_label": "중증 호흡곤란",
                "ktas": 2,
            },
            {
                "row_code": "CPBAD",
                "category_code": "P",
                "category_label": "일반",
                "complaint_code": "B",
                "complaint_label": "쏘임",
                "detail_code": "AD",
                "detail_label": "쇼크",
                "ktas": 1,
            },
        ]
        self.result = build_index(
            self.rows,
            aliases={
                "O:F": {
                    "canonical_terms": ["저체온증", "hypothermia"],
                    "aliases": ["저체온", "몸이 차갑다"],
                }
            },
            feature_hints={"AA|중증 호흡곤란": ["SpO2 저하", "청색증"]},
        )

    def test_builds_hierarchy_and_stable_keys(self) -> None:
        complaints = self.result["categories"][0]["complaints"]
        self.assertEqual("O:F", complaints[0]["complaint_key"])
        self.assertEqual("O:F:AA", complaints[0]["details"][0]["detail_key"])
        self.assertEqual(
            "환경손상 > 저체온증 > 중증 호흡곤란",
            complaints[0]["details"][0]["canonical_path"],
        )
        self.assertEqual(
            {
                "category_count": 2,
                "complaint_count": 3,
                "detail_row_count": 3,
                "unique_criterion_count": 3,
            },
            self.result["stats"],
        )

    def test_routing_text_respects_stage_boundaries(self) -> None:
        category_text = self.result["category_index"][0]["routing_text"]
        complaint_text = next(
            item["routing_text"]
            for item in self.result["complaint_index"]
            if item["complaint_key"] == "O:F"
        )
        detail = next(
            item
            for item in self.result["detail_index"]
            if item["detail_key"] == "O:F:AA"
        )

        for forbidden in ("중증 호흡곤란", "SpO2 저하", "KTAS", " 1"):
            self.assertNotIn(forbidden, category_text)
            self.assertNotIn(forbidden, complaint_text)
        self.assertIn("저체온", complaint_text)
        self.assertIn("SpO2 저하", detail["routing_text"])
        self.assertNotIn("KTAS", detail["routing_text"])
        self.assertNotIn(" 1", detail["routing_text"])
        self.assertEqual(1, detail["ktas"])

    def test_normalizes_collision_labels_and_keeps_row_code_evidence(self) -> None:
        complaint_collisions = self.result["complaint_label_collision_index"]
        detail_collisions = self.result["detail_label_collision_index"]

        self.assertIn("저체온증", complaint_collisions)
        self.assertNotIn(" 저체온증 ", complaint_collisions)
        self.assertEqual(2, len(complaint_collisions["저체온증"]))
        self.assertIn("중증 호흡곤란", detail_collisions)
        self.assertEqual(
            {"COFAA", "CPFAA"},
            {
                evidence["row_code"]
                for evidence in detail_collisions["중증 호흡곤란"]
            },
        )

        criterion = self.result["criterion_index"]["AA|중증 호흡곤란|1"]
        self.assertEqual("COFAA", criterion[0]["row_code"])
        self.assertEqual("O:F:AA", criterion[0]["detail_key"])


class AuxiliaryDataTests(unittest.TestCase):
    @staticmethod
    def write_json(directory: str, content: str) -> Path:
        path = Path(directory) / "data.json"
        path.write_text(content, encoding="utf-8")
        return path

    def test_loads_valid_aliases_and_feature_hints(self) -> None:
        with TemporaryDirectory() as directory:
            aliases_path = self.write_json(
                directory,
                '{"O:F":{"canonical_terms":["저체온증"],"aliases":["저체온"]}}',
            )
            aliases = load_aliases(aliases_path)
            aliases_path.unlink()
            hints_path = self.write_json(
                directory,
                '{"AA|중증 호흡곤란":["SpO2 저하"]}',
            )
            hints = load_feature_hints(hints_path)

        self.assertEqual(["저체온"], aliases["O:F"]["aliases"])
        self.assertEqual(["SpO2 저하"], hints["AA|중증 호흡곤란"])

    def test_rejects_invalid_auxiliary_shapes_with_key_name(self) -> None:
        with TemporaryDirectory() as directory:
            aliases_path = self.write_json(
                directory,
                '{"O:F":{"canonical_terms":"저체온증","aliases":[]}}',
            )
            with self.assertRaisesRegex(ValueError, "O:F"):
                load_aliases(aliases_path)

            aliases_path.unlink()
            hints_path = self.write_json(
                directory,
                '{"AA|중증 호흡곤란":"SpO2 저하"}',
            )
            with self.assertRaisesRegex(ValueError, "AA\\|중증 호흡곤란"):
                load_feature_hints(hints_path)


if __name__ == "__main__":
    unittest.main()
