from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Generic, Iterable, List, Optional, Protocol, Sequence, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class AdjacentSigungu:
    neighbor_sigungu_code: str
    neighbor_sigungu_name: str
    neighbor_sido_code: str
    adjacency_type: str
    touches: bool
    centroid_distance_km: float


@dataclass(frozen=True)
class ExpansionPolicy:
    top_touching_limit: int = 3
    include_remaining_touches: bool = True
    include_buffer_intersects: bool = True


@dataclass(frozen=True)
class SigunguAdjacencyIndex:
    neighbors_by_code: Dict[str, List[AdjacentSigungu]]
    code_to_name: Dict[str, str]
    code_to_sido_code: Dict[str, str]
    name_to_code: Dict[str, str]

    @property
    def all_codes(self) -> List[str]:
        return sorted(self.neighbors_by_code.keys())

    def get_name(self, sigungu_code: str) -> Optional[str]:
        return self.code_to_name.get(sigungu_code)

    def get_code(self, sigungu_name: str) -> Optional[str]:
        return self.name_to_code.get(_normalize_name(sigungu_name))

    def get_sido_code(self, sigungu_code: str) -> Optional[str]:
        return self.code_to_sido_code.get(sigungu_code)


@dataclass(frozen=True)
class ProgressiveSearchAttempt:
    level: int
    sigungu_code: str
    sigungu_name: Optional[str]
    fetch_status: str
    raw_count: int
    fetched_count: int
    valid_count: int
    error: Optional[str] = None


@dataclass(frozen=True)
class ProgressiveSearchResult(Generic[T]):
    items: List[T]
    attempts: List[ProgressiveSearchAttempt]


@dataclass(frozen=True)
class ResolvedSigungu:
    sigungu_code: str
    sigungu_name: str
    sido_code: Optional[str] = None
    sido_name: Optional[str] = None


class SigunguResolver(Protocol):
    def resolve(self, lat: float, lon: float) -> Optional[ResolvedSigungu]:
        ...


def _normalize_name(name: str) -> str:
    return name.strip().replace(" ", "")


def _derive_sido_code(sigungu_code: str) -> Optional[str]:
    code = str(sigungu_code).strip()
    if len(code) >= 2 and code[:2].isdigit():
        return code[:2]
    return None


def load_sigungu_adjacency(path: str | Path) -> SigunguAdjacencyIndex:
    src = Path(path)
    raw = json.loads(src.read_text(encoding="utf-8"))

    neighbors_by_code: Dict[str, List[AdjacentSigungu]] = {}
    code_to_name: Dict[str, str] = {}
    code_to_sido_code: Dict[str, str] = {}

    for base_code, raw_neighbors in raw.items():
        base_code_str = str(base_code)
        derived_base_sido_code = _derive_sido_code(base_code_str)
        if derived_base_sido_code:
            code_to_sido_code.setdefault(base_code_str, derived_base_sido_code)

        parsed: List[AdjacentSigungu] = []
        for item in raw_neighbors:
            neighbor = AdjacentSigungu(
                neighbor_sigungu_code=str(item["neighbor_sigungu_code"]),
                neighbor_sigungu_name=str(item["neighbor_sigungu_name"]),
                neighbor_sido_code=str(item["neighbor_sido_code"]),
                adjacency_type=str(item["adjacency_type"]),
                touches=bool(item["touches"]),
                centroid_distance_km=float(item["centroid_distance_km"]),
            )
            parsed.append(neighbor)
            code_to_name.setdefault(
                neighbor.neighbor_sigungu_code,
                neighbor.neighbor_sigungu_name,
            )
            derived_neighbor_sido_code = _derive_sido_code(neighbor.neighbor_sigungu_code)
            if derived_neighbor_sido_code:
                code_to_sido_code.setdefault(
                    neighbor.neighbor_sigungu_code,
                    derived_neighbor_sido_code,
                )
            else:
                code_to_sido_code.setdefault(
                    neighbor.neighbor_sigungu_code,
                    neighbor.neighbor_sido_code,
                )
        neighbors_by_code[base_code_str] = parsed

    name_to_code = {_normalize_name(name): code for code, name in code_to_name.items()}
    return SigunguAdjacencyIndex(
        neighbors_by_code=neighbors_by_code,
        code_to_name=code_to_name,
        code_to_sido_code=code_to_sido_code,
        name_to_code=name_to_code,
    )


def build_expansion_levels(
    base_code: str,
    adjacency_index: SigunguAdjacencyIndex,
    policy: ExpansionPolicy | None = None,
    fallback_codes: Optional[Iterable[str]] = None,
) -> List[List[str]]:
    cfg = policy or ExpansionPolicy()
    seen = {base_code}
    levels: List[List[str]] = [[base_code]]

    neighbors = sorted(
        adjacency_index.neighbors_by_code.get(base_code, []),
        key=lambda item: (item.centroid_distance_km, item.neighbor_sigungu_code),
    )

    touching = [
        item for item in neighbors if item.touches and item.adjacency_type == "border_touch"
    ]
    non_touching = [
        item
        for item in neighbors
        if item.neighbor_sigungu_code not in {n.neighbor_sigungu_code for n in touching}
    ]

    top_touching = [
        item.neighbor_sigungu_code
        for item in touching[: cfg.top_touching_limit]
        if item.neighbor_sigungu_code not in seen
    ]
    if top_touching:
        seen.update(top_touching)
        levels.append(top_touching)

    if cfg.include_remaining_touches:
        remaining_touching = [
            item.neighbor_sigungu_code
            for item in touching[cfg.top_touching_limit :]
            if item.neighbor_sigungu_code not in seen
        ]
        if remaining_touching:
            seen.update(remaining_touching)
            levels.append(remaining_touching)

    if cfg.include_buffer_intersects:
        buffered = [
            item.neighbor_sigungu_code
            for item in non_touching
            if item.neighbor_sigungu_code not in seen
        ]
        if buffered:
            seen.update(buffered)
            levels.append(buffered)

    if fallback_codes:
        fallback = [code for code in fallback_codes if code not in seen]
        if fallback:
            levels.append(fallback)

    return levels


def expand_sigungu(
    base_code: str,
    adjacency_index: SigunguAdjacencyIndex,
    policy: ExpansionPolicy | None = None,
    fallback_codes: Optional[Iterable[str]] = None,
) -> List[str]:
    ordered: List[str] = []
    for level_codes in build_expansion_levels(
        base_code=base_code,
        adjacency_index=adjacency_index,
        policy=policy,
        fallback_codes=fallback_codes,
    ):
        ordered.extend(level_codes)
    return ordered


def search_regions_progressively(
    levels: Sequence[Sequence[str]],
    fetch_valid_items: Callable[[str], Sequence[T]],
    item_key: Callable[[T], str],
    min_valid_items: int,
    code_to_name: Optional[Dict[str, str]] = None,
) -> ProgressiveSearchResult[T]:
    items_by_key: Dict[str, T] = {}
    attempts: List[ProgressiveSearchAttempt] = []

    for level_idx, codes in enumerate(levels):
        for code in codes:
            try:
                fetched_items = list(fetch_valid_items(code))
                for item in fetched_items:
                    items_by_key.setdefault(item_key(item), item)
                attempts.append(
                    ProgressiveSearchAttempt(
                        level=level_idx,
                        sigungu_code=code,
                        sigungu_name=(code_to_name or {}).get(code),
                        fetch_status="success",
                        raw_count=len(fetched_items),
                        fetched_count=len(fetched_items),
                        valid_count=len(items_by_key),
                    )
                )
            except Exception as exc:
                attempts.append(
                    ProgressiveSearchAttempt(
                        level=level_idx,
                        sigungu_code=code,
                        sigungu_name=(code_to_name or {}).get(code),
                        fetch_status="error",
                        raw_count=0,
                        fetched_count=0,
                        valid_count=len(items_by_key),
                        error=str(exc),
                    )
                )

            if len(items_by_key) >= min_valid_items:
                return ProgressiveSearchResult(
                    items=list(items_by_key.values()),
                    attempts=attempts,
                )

    return ProgressiveSearchResult(items=list(items_by_key.values()), attempts=attempts)
