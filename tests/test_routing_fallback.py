from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import requests

from app.main import (
    GlobalFallbackResult,
    MAX_GLOBAL_FALLBACK_SIGUNGU,
    _merge_candidates_by_hpid,
    _run_global_fallback,
    route_from_ktas_seoul,
)
from app.schemas import KTASRoutingRequest, RoutingCandidateHospital
from app.services.sigungu_search import ProgressiveSearchResult


def candidate(hpid: str) -> RoutingCandidateHospital:
    return RoutingCandidateHospital(
        id=hpid,
        name=hpid,
        address="Seoul",
        phone=None,
        emergency_phone=None,
        latitude=37.5,
        longitude=127.0,
        procedure_beds={"cardiac": {"api_beds": 1, "effective_beds": 1}},
        total_effective_beds=1,
        has_any_bed=True,
        groups_with_beds=["cardiac"],
        groups_with_beds_labels=["cardiac"],
        supported_complaints=[1],
        supported_complaint_labels=["chest pain"],
        mkiosk_flags=[],
        coverage_score=1.0,
        coverage_level="FULL",
        priority_score=1.0,
        reason_summary="available",
    )


def request() -> KTASRoutingRequest:
    return KTASRoutingRequest(
        ktas_level=2,
        chief_complaint="chest_pain",
        current_sigungu_code="11110",
    )


class RouteFallbackPolicyTests(unittest.TestCase):
    def _route(self, candidates: list[RoutingCandidateHospital], fallback: GlobalFallbackResult):
        progressive = ProgressiveSearchResult(items=candidates, attempts=[])
        with (
            patch("app.main._resolve_current_region", return_value=("11110", "서울특별시")),
            patch(
                "app.main._search_routing_candidates_progressively",
                return_value=(candidates, progressive),
            ),
            patch("app.main._run_global_fallback", return_value=fallback) as run_fallback,
        ):
            response = route_from_ktas_seoul(request())
        return response, run_fallback

    def test_three_candidates_return_complete_without_global_fallback(self) -> None:
        candidates = [candidate("A1"), candidate("A2"), candidate("A3")]
        response, run_fallback = self._route(candidates, GlobalFallbackResult())

        self.assertEqual(response.search_status, "complete")
        self.assertFalse(response.fallback_used)
        run_fallback.assert_not_called()

    def test_partial_candidates_do_not_run_global_fallback(self) -> None:
        candidates = [candidate("A1"), candidate("A2")]
        response, run_fallback = self._route(candidates, GlobalFallbackResult())

        self.assertEqual(response.search_status, "partial_candidates")
        self.assertEqual([item.id for item in response.hospitals], ["A1", "A2"])
        self.assertFalse(response.fallback_used)
        run_fallback.assert_not_called()

    def test_zero_candidates_run_global_fallback_and_return_partial_result(self) -> None:
        fallback = GlobalFallbackResult(
            candidates=[candidate("A9")],
            reason="sigungu_budget_exhausted",
        )
        response, run_fallback = self._route([], fallback)

        run_fallback.assert_called_once()
        self.assertEqual(response.search_status, "fallback_partial")
        self.assertTrue(response.fallback_used)
        self.assertEqual([item.id for item in response.hospitals], ["A9"])


class BoundedGlobalFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adjacency = Mock()
        self.adjacency.all_codes = ["11110", "11120", "11130"]
        self.adjacency.get_name.side_effect = lambda code: f"name-{code}"
        self.adjacency.get_sido_code.return_value = "11"

    def test_429_stops_after_first_region_and_redacts_service_key(self) -> None:
        response = Mock(status_code=429)
        error = requests.HTTPError(
            "429 for url?serviceKey=raw-secret&x=1",
            response=response,
        )
        with (
            patch("app.main._get_sigungu_adjacency_index", return_value=self.adjacency),
            patch("app.main.get_hospital_summaries_by_region", side_effect=error) as fetch,
        ):
            result = _run_global_fallback(request(), 1, ["cardiac"], "chest pain")

        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(result.reason, "rate_limited")
        self.assertNotIn("raw-secret", " ".join(result.warnings))

    def test_repeated_timeouts_stop_fallback(self) -> None:
        with (
            patch("app.main._get_sigungu_adjacency_index", return_value=self.adjacency),
            patch(
                "app.main.get_hospital_summaries_by_region",
                side_effect=requests.Timeout("Read timed out"),
            ) as fetch,
        ):
            result = _run_global_fallback(request(), 1, ["cardiac"], "chest pain")

        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(result.reason, "timeout_budget_exhausted")

    def test_fallback_skips_emergency_messages(self) -> None:
        with (
            patch("app.main._get_sigungu_adjacency_index", return_value=self.adjacency),
            patch("app.main.get_hospital_summaries_by_region", return_value=[]) as fetch,
        ):
            _run_global_fallback(request(), 1, ["cardiac"], "chest pain")

        self.assertFalse(fetch.call_args.kwargs["include_messages"])

    def test_sigungu_budget_limits_empty_region_queries(self) -> None:
        self.adjacency.all_codes = [f"11{index:03d}" for index in range(10)]
        with (
            patch("app.main._get_sigungu_adjacency_index", return_value=self.adjacency),
            patch("app.main.get_hospital_summaries_by_region", return_value=[]) as fetch,
        ):
            result = _run_global_fallback(request(), 1, ["cardiac"], "chest pain")

        self.assertEqual(fetch.call_count, MAX_GLOBAL_FALLBACK_SIGUNGU)
        self.assertEqual(result.reason, "sigungu_budget_exhausted")

    def test_merge_preserves_existing_candidate_and_deduplicates_hpid(self) -> None:
        existing = candidate("A1")
        duplicate = candidate("A1")
        duplicate.name = "replacement"

        merged = _merge_candidates_by_hpid(
            [existing],
            [duplicate, candidate("A2")],
        )

        self.assertEqual({item.id for item in merged}, {"A1", "A2"})
        self.assertIs(next(item for item in merged if item.id == "A1"), existing)


if __name__ == "__main__":
    unittest.main()
