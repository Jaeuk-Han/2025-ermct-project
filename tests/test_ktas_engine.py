from __future__ import annotations

import unittest
from unittest.mock import patch

from app.ktas_engine import classify_ktas, run_ktas_engine


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

    def test_run_ktas_engine_defaults_to_rule_based_method(self) -> None:
        sbar = minimal_sbar({"mental_status": "alert"})

        with (
            patch("app.ktas_engine.call_llm2_for_sbar", return_value=__import__("json").dumps(sbar)),
            self.assertLogs("app.ktas_engine", level="INFO") as logs,
        ):
            result = run_ktas_engine("dyspnea patient")

        self.assertEqual(result["ktas_method"], "rule_based")
        self.assertEqual(result["method"], "rule_based")
        self.assertIsNone(result.get("fallback_from"))
        self.assertIsNone(result.get("fallback_reason"))
        log_output = "\n".join(logs.output)
        self.assertIn("engine start use_rag=False", log_output)
        self.assertIn("engine result method=rule_based", log_output)
        self.assertNotIn("dyspnea patient", log_output)

    def test_run_ktas_engine_falls_back_to_rule_based_when_rag_index_missing(
        self,
    ) -> None:
        sbar = minimal_sbar({"mental_status": "alert", "spo2": 89})

        with (
            patch("app.ktas_engine.call_llm2_for_sbar", return_value=__import__("json").dumps(sbar)),
            self.assertLogs("app.ktas_engine", level="INFO") as logs,
        ):
            result = run_ktas_engine(
                "dyspnea patient",
                use_rag=True,
                rag_vector_store=None,
            )

        self.assertEqual(result["ktas"], 2)
        self.assertEqual(result["ktas_method"], "rule_based")
        self.assertEqual(result["method"], "rule_based")
        self.assertEqual(result["fallback_from"], "rag_based")
        self.assertIn("RAG", result["fallback_reason"])
        log_output = "\n".join(logs.output)
        self.assertIn("engine start use_rag=True", log_output)
        self.assertIn("fallback to rule_based", log_output)
        self.assertIn("engine result method=rule_based", log_output)
        self.assertNotIn("dyspnea patient", log_output)


if __name__ == "__main__":
    unittest.main()
