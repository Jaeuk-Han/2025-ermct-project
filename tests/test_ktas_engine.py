from __future__ import annotations

import unittest

from app.ktas_engine import classify_ktas


def minimal_sbar(assessment: dict) -> dict:
    return {
        "S": {
            "chief_complaint_group": "Respiratory",
            "chief_complaint": "dyspnea",
            "modifiers": [],
            "red_flags": [],
            "severity": "unknown",
            "requirement": None,
        },
        "B": {},
        "A": assessment,
        "R": {
            "oxygen": {
                "used": False,
                "device": None,
                "flow": None,
            },
            "drug": [],
            "cpr": False,
            "aed": False,
        },
    }


class KtasEngineTests(unittest.TestCase):
    def test_classify_ktas_skips_spo2_rule_when_spo2_missing(self) -> None:
        result = classify_ktas(minimal_sbar({"mental_status": "alert"}))

        self.assertEqual(result["ktas"], 3)

    def test_classify_ktas_skips_spo2_avpu_rule_when_avpu_missing(self) -> None:
        result = classify_ktas(
            minimal_sbar(
                {
                    "mental_status": "alert",
                    "spo2": 89,
                }
            )
        )

        self.assertEqual(result["ktas"], 2)
        self.assertIn("SpO2", result["reason"])


if __name__ == "__main__":
    unittest.main()
