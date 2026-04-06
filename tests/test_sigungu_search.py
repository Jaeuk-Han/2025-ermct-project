from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.services.sigungu_search import (
    ExpansionPolicy,
    build_expansion_levels,
    load_sigungu_adjacency,
    search_regions_progressively,
)


class SigunguSearchTests(unittest.TestCase):
    def _write_fixture(self) -> Path:
        payload = {
            "11110": [
                {
                    "neighbor_sigungu_code": "11120",
                    "neighbor_sigungu_name": "B-gu",
                    "neighbor_sido_code": "11",
                    "adjacency_type": "border_touch",
                    "touches": True,
                    "centroid_distance_km": 1.2,
                },
                {
                    "neighbor_sigungu_code": "11130",
                    "neighbor_sigungu_name": "C-gu",
                    "neighbor_sido_code": "11",
                    "adjacency_type": "border_touch",
                    "touches": True,
                    "centroid_distance_km": 2.4,
                },
                {
                    "neighbor_sigungu_code": "11140",
                    "neighbor_sigungu_name": "D-gu",
                    "neighbor_sido_code": "11",
                    "adjacency_type": "buffer_intersects",
                    "touches": False,
                    "centroid_distance_km": 3.0,
                },
            ],
            "11120": [
                {
                    "neighbor_sigungu_code": "11110",
                    "neighbor_sigungu_name": "A-gu",
                    "neighbor_sido_code": "11",
                    "adjacency_type": "border_touch",
                    "touches": True,
                    "centroid_distance_km": 1.2,
                }
            ],
        }
        temp_dir = Path(tempfile.mkdtemp())
        src = temp_dir / "adjacency.json"
        src.write_text(json.dumps(payload), encoding="utf-8")
        return src

    def test_build_expansion_levels_orders_touching_then_buffer(self) -> None:
        src = self._write_fixture()
        index = load_sigungu_adjacency(src)

        levels = build_expansion_levels(
            base_code="11110",
            adjacency_index=index,
            policy=ExpansionPolicy(top_touching_limit=1),
            fallback_codes=["11150"],
        )

        self.assertEqual(levels[0], ["11110"])
        self.assertEqual(levels[1], ["11120"])
        self.assertEqual(levels[2], ["11130"])
        self.assertEqual(levels[3], ["11140"])
        self.assertEqual(levels[4], ["11150"])

    def test_search_regions_progressively_distinguishes_error_and_valid_items(self) -> None:
        levels = [["11110"], ["11120"], ["11130"]]

        def fetch(code: str) -> list[str]:
            if code == "11110":
                return []
            if code == "11120":
                raise RuntimeError("upstream 502")
            return ["HOSPITAL-1", "HOSPITAL-2"]

        result = search_regions_progressively(
            levels=levels,
            fetch_valid_items=fetch,
            item_key=lambda item: item,
            min_valid_items=2,
            code_to_name={"11110": "A-gu", "11120": "B-gu", "11130": "C-gu"},
        )

        self.assertEqual(result.items, ["HOSPITAL-1", "HOSPITAL-2"])
        self.assertEqual(result.attempts[0].fetch_status, "success")
        self.assertEqual(result.attempts[0].fetched_count, 0)
        self.assertEqual(result.attempts[1].fetch_status, "error")
        self.assertEqual(result.attempts[2].valid_count, 2)


if __name__ == "__main__":
    unittest.main()
