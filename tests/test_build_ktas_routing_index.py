from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.build_ktas_routing_index import parse_rows


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


if __name__ == "__main__":
    unittest.main()
