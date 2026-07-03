from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
import math
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence


INDEX_VERSION = "ktas-detail-embedding-v1"
STRING_FIELDS = (
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


@dataclass(frozen=True)
class DetailEmbeddingItem:
    row_code: str
    detail_key: str
    category_code: str
    category_label: str
    complaint_code: str
    complaint_label: str
    detail_code: str
    detail_label: str
    canonical_path: str
    ktas: int
    routing_text: str
    embedding: tuple[float, ...]


class KtasDetailEmbeddingStore:
    def __init__(
        self,
        items: tuple[DetailEmbeddingItem, ...],
        groups: Mapping[tuple[str, str], tuple[DetailEmbeddingItem, ...]],
        embedding_dimension: int,
    ) -> None:
        self._items = items
        self._groups = MappingProxyType(dict(groups))
        self.embedding_dimension = embedding_dimension

    @property
    def item_count(self) -> int:
        return len(self._items)

    @property
    def group_keys(self) -> tuple[tuple[str, str], ...]:
        return tuple(self._groups)

    def search(
        self,
        query_embedding: Sequence[float],
        category_code: str,
        complaint_code: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
            raise ValueError("top_k must be an integer greater than zero")
        if (
            not isinstance(query_embedding, Sequence)
            or isinstance(query_embedding, (str, bytes))
            or not query_embedding
            or not all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                for value in query_embedding
            )
        ):
            raise ValueError(
                "query_embedding must be a non-empty finite numeric vector"
            )
        query = tuple(float(value) for value in query_embedding)
        if self._items and len(query) != self.embedding_dimension:
            raise ValueError(
                "query embedding dimension mismatch: "
                f"expected {self.embedding_dimension}, got {len(query)}"
            )

        query_norm = math.sqrt(sum(value * value for value in query))
        results: list[dict[str, Any]] = []
        for item in self._groups.get((category_code, complaint_code), ()):
            item_norm = math.sqrt(sum(value * value for value in item.embedding))
            similarity = 0.0
            if query_norm and item_norm:
                similarity = sum(
                    left * right for left, right in zip(query, item.embedding)
                ) / (query_norm * item_norm)
            results.append(
                {
                    "row_code": item.row_code,
                    "detail_key": item.detail_key,
                    "category_code": item.category_code,
                    "complaint_code": item.complaint_code,
                    "canonical_path": item.canonical_path,
                    "detail_label": item.detail_label,
                    "ktas": item.ktas,
                    "similarity": similarity,
                }
            )
        results.sort(
            key=lambda result: (
                -result["similarity"],
                result["row_code"],
                result["detail_key"],
            )
        )
        return results[:top_k]

    @classmethod
    def load(cls, path: Path) -> "KtasDetailEmbeddingStore":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("index root must be an object")
        if payload.get("version") != INDEX_VERSION:
            raise ValueError(f"version must be {INDEX_VERSION!r}")
        stats = payload.get("stats")
        items_data = payload.get("items")
        if not isinstance(stats, dict):
            raise ValueError("stats must be an object")
        if not isinstance(items_data, list):
            raise ValueError("items must be an array")
        detail_row_count = stats.get("detail_row_count")
        if (
            not isinstance(detail_row_count, int)
            or isinstance(detail_row_count, bool)
            or detail_row_count < 0
        ):
            raise ValueError("stats.detail_row_count must be a non-negative integer")
        if detail_row_count != len(items_data):
            raise ValueError(
                "stats.detail_row_count does not match items count: "
                f"{detail_row_count} != {len(items_data)}"
            )

        parsed_items: list[DetailEmbeddingItem] = []
        dimension: int | None = None
        for index, raw in enumerate(items_data):
            item = cls._parse_item(raw, index, dimension)
            if dimension is None:
                dimension = len(item.embedding)
            parsed_items.append(item)
        items = tuple(parsed_items)
        resolved_dimension = dimension or 0
        grouped: defaultdict[tuple[str, str], list[DetailEmbeddingItem]] = defaultdict(list)
        for item in items:
            grouped[(item.category_code, item.complaint_code)].append(item)
        groups = {key: tuple(value) for key, value in grouped.items()}
        return cls(items, groups, resolved_dimension)

    @staticmethod
    def _parse_item(
        raw: Any,
        index: int,
        expected_dimension: int | None,
    ) -> DetailEmbeddingItem:
        prefix = f"items[{index}]"
        if not isinstance(raw, dict):
            raise ValueError(f"{prefix} must be an object")
        for field in STRING_FIELDS:
            value = raw.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{prefix}.{field} must be a non-empty string")
        ktas = raw.get("ktas")
        if not isinstance(ktas, int) or isinstance(ktas, bool):
            raise ValueError(f"{prefix}.ktas must be an integer")
        embedding = raw.get("embedding")
        if (
            not isinstance(embedding, list)
            or not embedding
            or not all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                for value in embedding
            )
        ):
            raise ValueError(
                f"{prefix}.embedding must be a non-empty finite numeric vector"
            )
        if expected_dimension is not None and len(embedding) != expected_dimension:
            raise ValueError(
                f"{prefix} embedding dimension mismatch: "
                f"expected {expected_dimension}, got {len(embedding)}"
            )
        return DetailEmbeddingItem(
            row_code=raw["row_code"],
            detail_key=raw["detail_key"],
            category_code=raw["category_code"],
            category_label=raw["category_label"],
            complaint_code=raw["complaint_code"],
            complaint_label=raw["complaint_label"],
            detail_code=raw["detail_code"],
            detail_label=raw["detail_label"],
            canonical_path=raw["canonical_path"],
            ktas=ktas,
            routing_text=raw["routing_text"],
            embedding=tuple(float(value) for value in embedding),
        )
