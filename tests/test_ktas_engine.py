from __future__ import annotations

import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.ktas_engine import classify_ktas, run_ktas_engine
from app.ktas_rag import RagKtasCandidate, RagResponseParseError


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
    def _run_with_rag(self, *, rule_level: int, rag_level: int, confidence: float, evidence: list[str]):
        sbar = minimal_sbar({"mental_status": "alert"})
        with (
            patch("app.ktas_engine.call_llm2_for_sbar", return_value=__import__("json").dumps(sbar)),
            patch(
                "app.ktas_engine.classify_ktas",
                return_value={"ktas": rule_level, "reason": "rule baseline"},
            ) as classify_rule,
            patch(
                "app.ktas_engine.classify_ktas_rag",
                return_value=[
                    {
                        "ktas": rag_level,
                        "reason": "rag result",
                        "confidence": confidence,
                        "evidence": evidence,
                    }
                ],
            ),
        ):
            result = run_ktas_engine("patient", use_rag=True, rag_vector_store=object())
        return result, classify_rule

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

    def test_valid_rag_keeps_method_and_adds_baseline_metadata(self) -> None:
        result, classify_rule = self._run_with_rag(
            rule_level=3,
            rag_level=3,
            confidence=0.8,
            evidence=["doc-1"],
        )

        classify_rule.assert_called_once()
        self.assertEqual(result["ktas_method"], "rag_based")
        self.assertEqual(result["rule_based_ktas"], 3)
        self.assertEqual(result["rag_based_ktas"], 3)
        self.assertEqual(result["rag_confidence"], 0.8)
        self.assertFalse(result["safety_merge_applied"])
        self.assertIsNone(result["fallback_reason"])

    def test_empty_evidence_uses_rule_baseline_but_keeps_rag_method(self) -> None:
        result, _ = self._run_with_rag(
            rule_level=3,
            rag_level=4,
            confidence=0.8,
            evidence=[],
        )

        self.assertEqual(result["ktas"], 3)
        self.assertEqual(result["ktas_method"], "rag_based")
        self.assertTrue(result["safety_merge_applied"])
        self.assertEqual(result["fallback_reason"], "rag_evidence_empty")

    def test_low_confidence_uses_rule_baseline(self) -> None:
        result, _ = self._run_with_rag(
            rule_level=3,
            rag_level=4,
            confidence=0.59,
            evidence=["doc-1"],
        )

        self.assertEqual(result["ktas"], 3)
        self.assertEqual(result["ktas_method"], "rag_based")
        self.assertTrue(result["safety_merge_applied"])
        self.assertEqual(result["fallback_reason"], "rag_confidence_low")

    def test_rule_three_allows_supported_rag_four(self) -> None:
        result, _ = self._run_with_rag(
            rule_level=3,
            rag_level=4,
            confidence=0.9,
            evidence=["doc-1"],
        )

        self.assertEqual(result["ktas"], 4)
        self.assertFalse(result["safety_merge_applied"])
        self.assertIsNone(result["fallback_reason"])

    def test_rule_three_allows_supported_rag_five(self) -> None:
        result, _ = self._run_with_rag(
            rule_level=3,
            rag_level=5,
            confidence=0.9,
            evidence=["doc-1"],
        )

        self.assertEqual(result["ktas"], 5)
        self.assertFalse(result["safety_merge_applied"])
        self.assertIsNone(result["fallback_reason"])

    def test_rag_one_to_three_still_uses_more_urgent_value(self) -> None:
        result, _ = self._run_with_rag(
            rule_level=3,
            rag_level=2,
            confidence=0.9,
            evidence=["doc-1"],
        )

        self.assertEqual(result["ktas"], 2)
        self.assertFalse(result["safety_merge_applied"])
        self.assertIsNone(result["fallback_reason"])

        result, _ = self._run_with_rag(
            rule_level=2,
            rag_level=3,
            confidence=0.9,
            evidence=["doc-1"],
        )

        self.assertEqual(result["ktas"], 2)
        self.assertTrue(result["safety_merge_applied"])
        self.assertEqual(result["fallback_reason"], "rag_less_urgent_than_rule")

    def test_rule_one_overrides_supported_rag_four_as_safety_signal(self) -> None:
        result, _ = self._run_with_rag(
            rule_level=1,
            rag_level=4,
            confidence=0.9,
            evidence=["doc-1"],
        )

        self.assertEqual(result["ktas"], 1)
        self.assertTrue(result["safety_merge_applied"])
        self.assertEqual(result["fallback_reason"], "rule_based_safety_priority")

    def test_rule_two_overrides_supported_rag_five_as_safety_signal(self) -> None:
        result, _ = self._run_with_rag(
            rule_level=2,
            rag_level=5,
            confidence=0.9,
            evidence=["doc-1"],
        )

        self.assertEqual(result["ktas"], 2)
        self.assertTrue(result["safety_merge_applied"])
        self.assertEqual(result["fallback_reason"], "rule_based_safety_priority")

    def test_rag_parse_failure_preserves_rule_based_fallback_contract(self) -> None:
        sbar = minimal_sbar({"mental_status": "alert"})
        with (
            patch("app.ktas_engine.call_llm2_for_sbar", return_value=__import__("json").dumps(sbar)),
            patch("app.ktas_engine.classify_ktas", return_value={"ktas": 3, "reason": "rule"}),
            patch(
                "app.ktas_engine.classify_ktas_rag",
                side_effect=RagResponseParseError("RAG output JSON parsing failed"),
            ),
        ):
            result = run_ktas_engine("patient", use_rag=True, rag_vector_store=object())

        self.assertEqual(result["ktas_method"], "rule_based")
        self.assertEqual(result["fallback_from"], "rag_based")
        self.assertEqual(result["fallback_reason"], "rag_parse_failed")
        self.assertTrue(result["safety_merge_applied"])

    def test_rag_validation_failure_uses_stable_reason(self) -> None:
        sbar = minimal_sbar({"mental_status": "alert"})
        try:
            RagKtasCandidate.model_validate(
                {"ktas": 6, "confidence": 0.8, "evidence": ["doc-1"]}
            )
        except ValidationError as exc:
            validation_error = exc
        with (
            patch("app.ktas_engine.call_llm2_for_sbar", return_value=__import__("json").dumps(sbar)),
            patch("app.ktas_engine.classify_ktas", return_value={"ktas": 3, "reason": "rule"}),
            patch("app.ktas_engine.classify_ktas_rag", side_effect=validation_error),
        ):
            result = run_ktas_engine("patient", use_rag=True, rag_vector_store=object())

        self.assertEqual(result["ktas_method"], "rule_based")
        self.assertEqual(result["fallback_reason"], "rag_validation_failed")

    def test_empty_rag_candidate_list_is_validation_failure(self) -> None:
        sbar = minimal_sbar({"mental_status": "alert"})
        with (
            patch("app.ktas_engine.call_llm2_for_sbar", return_value=__import__("json").dumps(sbar)),
            patch("app.ktas_engine.classify_ktas", return_value={"ktas": 3, "reason": "rule"}),
            patch("app.ktas_engine.classify_ktas_rag", return_value=[]),
        ):
            result = run_ktas_engine("patient", use_rag=True, rag_vector_store=object())

        self.assertEqual(result["fallback_reason"], "rag_validation_failed")


if __name__ == "__main__":
    unittest.main()
