from __future__ import annotations

import unittest

from pydantic import ValidationError

from app.ktas_rag import normalize_candidate, parse_rag_response


class RagResponseParserTests(unittest.TestCase):
    def test_parses_direct_json_object(self) -> None:
        parsed = parse_rag_response(
            '{"ktas_level": 3, "confidence": 0.72, "evidence": ["doc-1"]}'
        )

        self.assertEqual(parsed[0]["ktas_level"], 3)

    def test_parses_markdown_fenced_json(self) -> None:
        parsed = parse_rag_response(
            '```json\n{"ktas_level": 3, "confidence": 0.72, "evidence": ["doc-1"]}\n```'
        )

        self.assertEqual(parsed[0]["ktas_level"], 3)

    def test_extracts_json_object_from_surrounding_explanation(self) -> None:
        parsed = parse_rag_response(
            '판단 결과입니다.\n{"ktas_level": 3, "confidence": 0.72, "evidence": ["doc-1"]}\n이상입니다.'
        )

        self.assertEqual(parsed[0]["ktas_level"], 3)

    def test_malformed_response_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            parse_rag_response("not JSON at all")


class RagCandidateValidationTests(unittest.TestCase):
    def test_accepts_string_ktas_level_and_primary_reason_alias(self) -> None:
        normalized = normalize_candidate(
            {
                "ktas_level": "3",
                "primary_reason": "호흡 상태",
                "confidence": 0.8,
                "evidence": ["doc-1"],
            },
            top_similarity=0.9,
        )

        self.assertEqual(normalized["ktas"], 3)
        self.assertEqual(normalized["reason"], "호흡 상태")

    def test_accepts_legacy_ktas_and_reason_fields(self) -> None:
        normalized = normalize_candidate(
            {
                "ktas": 2,
                "reason": "red flag",
                "confidence": 0.9,
                "evidence": ["doc-1"],
            },
            top_similarity=0.9,
        )

        self.assertEqual(normalized["ktas"], 2)

    def test_rejects_ktas_outside_one_to_five(self) -> None:
        for level in (0, 6):
            with self.subTest(level=level), self.assertRaises(ValidationError):
                normalize_candidate(
                    {
                        "ktas_level": level,
                        "confidence": 0.8,
                        "evidence": ["doc-1"],
                    },
                    top_similarity=0.9,
                )

    def test_rejects_confidence_outside_zero_to_one_without_clamping(self) -> None:
        for confidence in (-0.1, 1.1):
            with self.subTest(confidence=confidence), self.assertRaises(ValidationError):
                normalize_candidate(
                    {
                        "ktas_level": 3,
                        "confidence": confidence,
                        "evidence": ["doc-1"],
                    },
                    top_similarity=0.9,
                )

    def test_rejects_non_list_evidence(self) -> None:
        with self.assertRaises(ValidationError):
            normalize_candidate(
                {
                    "ktas_level": 3,
                    "confidence": 0.8,
                    "evidence": "doc-1",
                },
                top_similarity=0.9,
            )

    def test_empty_evidence_is_structurally_valid(self) -> None:
        normalized = normalize_candidate(
            {"ktas_level": 3, "confidence": 0.8, "evidence": []},
            top_similarity=0.9,
        )

        self.assertEqual(normalized["evidence"], [])


if __name__ == "__main__":
    unittest.main()
