from __future__ import annotations

import unittest

from fastapi import HTTPException

from app.main import TextKTASRequest, _build_stage1_response


class Stage1ResponseTests(unittest.TestCase):
    def test_text_ktas_request_defaults_to_rule_based(self) -> None:
        request = TextKTASRequest(text="환자 호흡곤란")

        self.assertEqual(request.ktas_method, "rule_based")

    def test_stage1_response_normalizes_neuro_alias_without_zero_complaint_id(
        self,
    ) -> None:
        response = _build_stage1_response(
            {
                "ktas": 2,
                "chief_complaint": "acute focal weakness",
                "sbar": {"A": {"spo2": 94}},
            }
        )

        self.assertEqual(response.case.complaint_id, 3)
        self.assertNotEqual(response.case.complaint_id, 0)
        self.assertEqual(response.case.required_procedure_groups, ["ACS_STROKE", "BRAIN_HEMORRHAGE"])

    def test_stage1_response_normalizes_low_back_pain_without_zero_complaint_id(
        self,
    ) -> None:
        response = _build_stage1_response(
            {
                "ktas": 3,
                "chief_complaint": "low back pain",
                "sbar": {"A": {}},
            }
        )

        self.assertEqual(response.case.complaint_id, 7)
        self.assertNotEqual(response.case.complaint_id, 0)

    def test_stage1_response_rejects_unknown_complaint_instead_of_returning_zero(
        self,
    ) -> None:
        with self.assertRaises(HTTPException) as cm:
            _build_stage1_response(
                {
                    "ktas": 3,
                    "chief_complaint": "unknown label",
                    "sbar": {"A": {}},
                }
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.detail["reason"], "unknown_chief_complaint")

    def test_stage1_response_preserves_additive_ktas_metadata(self) -> None:
        response = _build_stage1_response(
            {
                "ktas": 2,
                "chief_complaint": "dyspnea",
                "reason": "rule fallback",
                "sbar": {"A": {"spo2": 89}},
                "ktas_method": "rule_based",
                "confidence": 0.75,
                "evidence": ["prektas-1"],
                "ktas_options": [
                    {
                        "ktas": 2,
                        "reason": "RAG candidate",
                        "confidence": 0.75,
                        "evidence": ["prektas-1"],
                    }
                ],
                "fallback_from": "rag_based",
                "fallback_reason": "RAG index not found",
            }
        )

        self.assertEqual(response.ktas_method, "rule_based")
        self.assertEqual(response.confidence, 0.75)
        self.assertEqual(response.evidence, ["prektas-1"])
        self.assertEqual(response.fallback_from, "rag_based")
        self.assertEqual(response.fallback_reason, "RAG index not found")
        self.assertEqual(response.ktas_options[0]["ktas"], 2)


if __name__ == "__main__":
    unittest.main()
