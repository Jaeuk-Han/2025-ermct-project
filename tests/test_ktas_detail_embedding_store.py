from __future__ import annotations

import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.ktas_detail_embedding_store import KtasDetailEmbeddingStore


class StoreFixtureMixin:
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def item(
        row_code: str,
        detail_key: str,
        category_code: str,
        complaint_code: str,
        embedding: list[float],
    ) -> dict:
        return {
            "row_code": row_code,
            "detail_key": detail_key,
            "category_code": category_code,
            "category_label": "호흡기",
            "complaint_code": complaint_code,
            "complaint_label": "호흡곤란",
            "detail_code": detail_key.rsplit(":", 1)[-1],
            "detail_label": f"기준 {row_code}",
            "canonical_path": f"호흡기 > 호흡곤란 > 기준 {row_code}",
            "ktas": 2,
            "routing_text": f"호흡기 호흡곤란 기준 {row_code}",
            "embedding": embedding,
        }

    def write_index(
        self,
        items: list[dict],
        *,
        version: str = "ktas-detail-embedding-v1",
        detail_row_count: int | None = None,
    ) -> Path:
        path = Path(self.temp.name) / "index.json"
        payload = {
            "version": version,
            "stats": {
                "detail_row_count": (
                    len(items) if detail_row_count is None else detail_row_count
                )
            },
            "items": items,
        }
        path.write_text(json.dumps(payload, allow_nan=True), encoding="utf-8")
        return path


class LoadStoreTests(StoreFixtureMixin, unittest.TestCase):
    def test_loads_valid_index_and_builds_immutable_groups(self) -> None:
        store = KtasDetailEmbeddingStore.load(
            self.write_index(
                [
                    self.item("CHAAA", "H:A:AA", "H", "A", [1.0, 0.0]),
                    self.item("CHBAA", "H:B:AA", "H", "B", [0.0, 1.0]),
                ]
            )
        )

        self.assertEqual(2, store.embedding_dimension)
        self.assertEqual(2, store.item_count)
        self.assertEqual({("H", "A"), ("H", "B")}, set(store.group_keys))

    def test_rejects_wrong_version(self) -> None:
        with self.assertRaisesRegex(ValueError, "version"):
            KtasDetailEmbeddingStore.load(
                self.write_index([], version="unsupported")
            )

    def test_rejects_stats_item_count_mismatch(self) -> None:
        with self.assertRaisesRegex(ValueError, "detail_row_count"):
            KtasDetailEmbeddingStore.load(
                self.write_index(
                    [self.item("CHAAA", "H:A:AA", "H", "A", [1.0])],
                    detail_row_count=2,
                )
            )


class ItemValidationTests(StoreFixtureMixin, unittest.TestCase):
    def test_rejects_each_missing_required_metadata_field(self) -> None:
        required = (
            "row_code",
            "detail_key",
            "category_code",
            "category_label",
            "complaint_code",
            "complaint_label",
            "detail_code",
            "detail_label",
            "canonical_path",
            "routing_text",
        )
        for field in required:
            with self.subTest(field=field):
                item = self.item("CHAAA", "H:A:AA", "H", "A", [1.0])
                item.pop(field)
                with self.assertRaisesRegex(ValueError, f"items\\[0\\].{field}"):
                    KtasDetailEmbeddingStore.load(self.write_index([item]))

    def test_rejects_invalid_ktas(self) -> None:
        for value in (True, "2", None):
            with self.subTest(value=value):
                item = self.item("CHAAA", "H:A:AA", "H", "A", [1.0])
                item["ktas"] = value
                with self.assertRaisesRegex(ValueError, "items\\[0\\].ktas"):
                    KtasDetailEmbeddingStore.load(self.write_index([item]))

    def test_rejects_empty_nonfinite_and_boolean_embedding_values(self) -> None:
        for embedding in ([], [math.nan], [math.inf], [True]):
            with self.subTest(embedding=embedding):
                with self.assertRaisesRegex(ValueError, "items\\[0\\].embedding"):
                    KtasDetailEmbeddingStore.load(
                        self.write_index(
                            [self.item("CHAAA", "H:A:AA", "H", "A", embedding)]
                        )
                    )

    def test_rejects_inconsistent_embedding_dimensions(self) -> None:
        with self.assertRaisesRegex(ValueError, "embedding dimension"):
            KtasDetailEmbeddingStore.load(
                self.write_index(
                    [
                        self.item("CHAAA", "H:A:AA", "H", "A", [1.0, 0.0]),
                        self.item("CHAAB", "H:A:AB", "H", "A", [1.0]),
                    ]
                )
            )


class SearchTests(StoreFixtureMixin, unittest.TestCase):
    def make_store(self) -> KtasDetailEmbeddingStore:
        return KtasDetailEmbeddingStore.load(
            self.write_index(
                [
                    self.item("CH003", "H:A:AC", "H", "A", [1.0, 0.0]),
                    self.item("CH001", "H:A:AB", "H", "A", [0.8, 0.6]),
                    self.item("CH001", "H:A:AA", "H", "A", [0.8, 0.6]),
                    self.item("CHB01", "H:B:AA", "H", "B", [1.0, 0.0]),
                    self.item("CH000", "H:A:AZ", "H", "A", [0.0, 0.0]),
                ]
            )
        )

    def test_rejects_invalid_top_k(self) -> None:
        store = self.make_store()
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "top_k"):
                    store.search([1.0, 0.0], "missing", "missing", value)

    def test_validates_query_before_group_lookup(self) -> None:
        store = self.make_store()
        for query, message in (
            ([], "query_embedding"),
            ([math.nan, 0.0], "query_embedding"),
            ([True, 0.0], "query_embedding"),
            ([1.0], "dimension"),
        ):
            with self.subTest(query=query):
                with self.assertRaisesRegex(ValueError, message):
                    store.search(query, "missing", "missing", 1)

    def test_filters_group_and_ranks_with_deterministic_ties(self) -> None:
        results = self.make_store().search([1.0, 0.0], "H", "A", top_k=4)

        self.assertEqual(
            ["CH003", "CH001", "CH001", "CH000"],
            [result["row_code"] for result in results],
        )
        self.assertEqual(
            ["H:A:AC", "H:A:AA", "H:A:AB", "H:A:AZ"],
            [result["detail_key"] for result in results],
        )
        self.assertNotIn("CHB01", [result["row_code"] for result in results])
        self.assertEqual(0.0, results[-1]["similarity"])
        self.assertEqual(
            {
                "row_code",
                "detail_key",
                "category_code",
                "complaint_code",
                "canonical_path",
                "detail_label",
                "ktas",
                "similarity",
            },
            set(results[0]),
        )

    def test_returns_empty_list_for_missing_group_with_valid_query(self) -> None:
        self.assertEqual(
            [],
            self.make_store().search([1.0, 0.0], "X", "Y", top_k=5),
        )


if __name__ == "__main__":
    unittest.main()
