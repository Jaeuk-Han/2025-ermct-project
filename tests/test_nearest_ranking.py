from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, patch

from app.distance_logic import calculate_all_distances_async, get_top3
from app.main import route_seoul_nearest
from app.schemas import (
    NearestRoutingRequest,
    RoutingCandidateHospital,
    RoutingCase,
)


def hospital(
    hpid: str,
    name: str,
    *,
    coverage: float,
    priority: float,
    beds: int,
) -> RoutingCandidateHospital:
    return RoutingCandidateHospital(
        id=hpid,
        name=name,
        address="Seoul",
        phone=None,
        emergency_phone=None,
        latitude=37.5,
        longitude=127.0,
        procedure_beds={"cardiac": {"api_beds": beds, "effective_beds": beds}},
        total_effective_beds=beds,
        has_any_bed=True,
        groups_with_beds=["cardiac"],
        groups_with_beds_labels=["cardiac"],
        supported_complaints=[1],
        supported_complaint_labels=["chest pain"],
        mkiosk_flags=[],
        coverage_score=coverage,
        coverage_level="HIGH" if coverage >= 0.75 else "LOW",
        priority_score=priority,
        reason_summary="available",
    )


def nearest_request(hospitals: list[RoutingCandidateHospital]) -> NearestRoutingRequest:
    return NearestRoutingRequest(
        followup_id=None,
        case=RoutingCase(
            ktas=2,
            complaint_id=1,
            complaint_label="chest pain",
            required_procedure_groups=["cardiac"],
            required_procedure_group_labels=["cardiac"],
        ),
        hospitals=hospitals,
        user_lat=37.5,
        user_lon=127.0,
    )


class DistanceRankingTests(unittest.IsolatedAsyncioTestCase):
    def test_distance_is_primary_sort_key(self) -> None:
        results = [
            {"id": "far", "distance": 2000, "duration_sec": 100, "coverage_score": 1.0, "priority_score": 99},
            {"id": "near", "distance": 1000, "duration_sec": 500, "coverage_score": 0.1, "priority_score": 1},
        ]

        self.assertEqual([item["id"] for item in get_top3(results)], ["near", "far"])

    def test_duration_breaks_equal_distance_tie_and_missing_duration_sorts_last(self) -> None:
        results = [
            {"id": "missing", "distance": 1000, "duration_sec": None, "coverage_score": 1.0, "priority_score": 99},
            {"id": "slow", "distance": 1000, "duration_sec": 500, "coverage_score": 1.0, "priority_score": 99},
            {"id": "fast", "distance": 1000, "duration_sec": 100, "coverage_score": 0.1, "priority_score": 1},
        ]

        self.assertEqual(
            [item["id"] for item in get_top3(results)],
            ["fast", "slow", "missing"],
        )

    def test_coverage_then_priority_break_remaining_ties(self) -> None:
        results = [
            {"id": "low", "distance": 1000, "duration_sec": 100, "coverage_score": 0.2, "priority_score": 99},
            {"id": "high-low-priority", "distance": 1000, "duration_sec": 100, "coverage_score": 0.8, "priority_score": 5},
            {"id": "high-high-priority", "distance": 1000, "duration_sec": 100, "coverage_score": 0.8, "priority_score": 7},
        ]

        self.assertEqual(
            [item["id"] for item in get_top3(results)],
            ["high-high-priority", "high-low-priority", "low"],
        )

    async def test_distance_results_preserve_hpid_metadata_and_exclude_failures(self) -> None:
        hospitals = [
            {
                "id": "A1",
                "name": "failed",
                "latitude": 37.1,
                "longitude": 127.1,
                "coverage_score": 0.2,
                "priority_score": 6.0,
            },
            {
                "id": "A2",
                "name": "success",
                "latitude": 37.2,
                "longitude": 127.2,
                "coverage_score": 0.8,
                "priority_score": 5.8,
            },
        ]
        with patch(
            "app.distance_logic.get_tmap_distance_async",
            new=AsyncMock(side_effect=[(None, None), (1000, 360)]),
        ):
            results = await calculate_all_distances_async(37.5, 127.0, hospitals)

        self.assertEqual(results, [{
            "id": "A2",
            "name": "success",
            "distance": 1000,
            "duration_sec": 360,
            "coverage_score": 0.8,
            "priority_score": 5.8,
            "reason_summary": "정보 없음",
        }])


class NearestEndpointOrderingTests(unittest.IsolatedAsyncioTestCase):
    async def test_severance_regression_returns_nearest_hospital_first(self) -> None:
        hospitals = [
            hospital("A1", "청구성심병원", coverage=0.2, priority=6.0, beds=8),
            hospital("A2", "세브란스병원", coverage=0.8, priority=5.8, beds=6),
            hospital("A3", "은평성모병원", coverage=0.2, priority=3.0, beds=4),
        ]
        distance_results = [
            {"id": "A1", "name": "청구성심병원", "distance": 9600, "duration_sec": 1740, "coverage_score": 0.2, "priority_score": 6.0},
            {"id": "A2", "name": "세브란스병원", "distance": 1000, "duration_sec": 360, "coverage_score": 0.8, "priority_score": 5.8},
            {"id": "A3", "name": "은평성모병원", "distance": 11400, "duration_sec": 1980, "coverage_score": 0.2, "priority_score": 3.0},
        ]
        with patch("app.main.calculate_all_distances_async", new=AsyncMock(return_value=distance_results)):
            response = await route_seoul_nearest(nearest_request(hospitals))

        self.assertEqual([item.id for item in response.hospitals], ["A2", "A1", "A3"])
        self.assertEqual(response.hospitals[0].duration_sec, 360)

    async def test_duplicate_names_map_by_hpid_and_partial_results_stay_stable(self) -> None:
        hospitals = [
            hospital("A1", "동명이원", coverage=0.2, priority=9.0, beds=8),
            hospital("A2", "동명이원", coverage=0.8, priority=5.0, beds=6),
            hospital("A3", "실패병원", coverage=1.0, priority=10.0, beds=9),
        ]
        distance_results = [
            {"id": "A2", "name": "동명이원", "distance": 1000, "duration_sec": 300, "coverage_score": 0.8, "priority_score": 5.0},
            {"id": "A1", "name": "동명이원", "distance": 2000, "duration_sec": 400, "coverage_score": 0.2, "priority_score": 9.0},
        ]
        with patch("app.main.calculate_all_distances_async", new=AsyncMock(return_value=distance_results)):
            response = await route_seoul_nearest(nearest_request(hospitals))

        self.assertEqual([item.id for item in response.hospitals], ["A2", "A1"])


if __name__ == "__main__":
    unittest.main()
