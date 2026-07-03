from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, TypedDict


FIELD_NAMES = (
    "row_code",
    "category_code",
    "category_label",
    "complaint_code",
    "complaint_label",
    "detail_code",
    "detail_label",
    "ktas",
)


class RoutingRow(TypedDict):
    row_code: str
    category_code: str
    category_label: str
    complaint_code: str
    complaint_label: str
    detail_code: str
    detail_label: str
    ktas: int


def _read_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def load_aliases(path: Path) -> dict[str, dict[str, list[str]]]:
    raw = _read_json_object(path)
    result: dict[str, dict[str, list[str]]] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            raise ValueError(f"invalid aliases entry for {key!r}: expected object")
        canonical_terms = value.get("canonical_terms", [])
        aliases = value.get("aliases", [])
        if not isinstance(canonical_terms, list) or not all(
            isinstance(item, str) for item in canonical_terms
        ):
            raise ValueError(
                f"invalid aliases entry for {key!r}: canonical_terms must be strings"
            )
        if not isinstance(aliases, list) or not all(
            isinstance(item, str) for item in aliases
        ):
            raise ValueError(
                f"invalid aliases entry for {key!r}: aliases must be strings"
            )
        result[key] = {
            "canonical_terms": canonical_terms,
            "aliases": aliases,
        }
    return result


def load_feature_hints(path: Path) -> dict[str, list[str]]:
    raw = _read_json_object(path)
    result: dict[str, list[str]] = {}
    for key, value in raw.items():
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ValueError(
                f"invalid feature hints entry for {key!r}: expected string array"
            )
        result[key] = value
    return result


def parse_rows(path: Path) -> tuple[list[RoutingRow], list[str]]:
    rows: list[RoutingRow] = []
    warnings: list[str] = []
    seen_row_codes: set[str] = set()
    seen_detail_keys: set[str] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, raw in enumerate(csv.reader(handle), start=1):
            if not raw or all(not cell.strip() for cell in raw):
                continue

            values = (raw + [""] * len(FIELD_NAMES))[: len(FIELD_NAMES)]
            if values == [str(index) for index in range(len(FIELD_NAMES))]:
                warnings.append(f"line {line_number}: skipped metadata row")
                continue
            record = {
                name: value.strip() for name, value in zip(FIELD_NAMES, values)
            }
            missing = [name for name in FIELD_NAMES[:-1] if not record[name]]
            if missing:
                warnings.append(
                    f"line {line_number}: missing required fields: {', '.join(missing)}"
                )
                continue

            try:
                ktas = int(record["ktas"])
            except ValueError:
                warnings.append(
                    f"line {line_number}: invalid ktas={record['ktas']!r}"
                )
                continue

            row_code = record["row_code"]
            parsed_detail_key = (
                f"{record['category_code']}:"
                f"{record['complaint_code']}:"
                f"{record['detail_code']}"
            )
            duplicate = False
            if row_code in seen_row_codes:
                warnings.append(f"line {line_number}: duplicate row_code={row_code}")
                duplicate = True
            if parsed_detail_key in seen_detail_keys:
                warnings.append(
                    f"line {line_number}: duplicate detail_key={parsed_detail_key}"
                )
                duplicate = True
            if duplicate:
                continue

            seen_row_codes.add(row_code)
            seen_detail_keys.add(parsed_detail_key)
            rows.append(
                RoutingRow(
                    row_code=row_code,
                    category_code=record["category_code"],
                    category_label=record["category_label"],
                    complaint_code=record["complaint_code"],
                    complaint_label=record["complaint_label"],
                    detail_code=record["detail_code"],
                    detail_label=record["detail_label"],
                    ktas=ktas,
                )
            )

    return rows, warnings


def complaint_key(row: Mapping[str, Any]) -> str:
    return f"{row['category_code']}:{row['complaint_code']}"


def detail_key(row: Mapping[str, Any]) -> str:
    return f"{complaint_key(row)}:{row['detail_code']}"


def join_text(parts: Iterable[str]) -> str:
    return " ".join(
        dict.fromkeys(part.strip() for part in parts if part and part.strip())
    )


def build_index(
    rows: list[RoutingRow],
    aliases: Mapping[str, Mapping[str, list[str]]],
    feature_hints: Mapping[str, list[str]],
) -> dict[str, Any]:
    normalized_rows = [
        {
            **row,
            "category_label": row["category_label"].strip(),
            "complaint_label": row["complaint_label"].strip(),
            "detail_label": row["detail_label"].strip(),
        }
        for row in rows
    ]
    normalized_rows.sort(
        key=lambda row: (
            row["category_code"],
            row["complaint_code"],
            row["detail_code"],
            row["row_code"],
        )
    )

    details: list[dict[str, Any]] = []
    complaints: dict[str, dict[str, Any]] = {}
    categories: dict[str, dict[str, Any]] = {}
    criterion_index: dict[str, list[dict[str, str]]] = {}
    complaint_labels: dict[str, dict[str, dict[str, str]]] = {}
    detail_labels: dict[str, dict[str, dict[str, str]]] = {}

    for row in normalized_rows:
        row_complaint_key = complaint_key(row)
        row_detail_key = detail_key(row)
        complaint_path = (
            f"{row['category_label']} > {row['complaint_label']}"
        )
        canonical_path = f"{complaint_path} > {row['detail_label']}"
        hint_key = f"{row['detail_code']}|{row['detail_label']}"
        hints = list(feature_hints.get(hint_key, []))
        detail = {
            "detail_key": row_detail_key,
            "row_code": row["row_code"],
            "category_code": row["category_code"],
            "category_label": row["category_label"],
            "complaint_code": row["complaint_code"],
            "complaint_label": row["complaint_label"],
            "detail_code": row["detail_code"],
            "detail_label": row["detail_label"],
            "canonical_path": canonical_path,
            "ktas": row["ktas"],
            "feature_hints": hints,
            "routing_text": join_text(
                [
                    row["category_label"],
                    row["complaint_label"],
                    row["detail_label"],
                    *hints,
                ]
            ),
        }
        details.append(detail)

        complaint = complaints.setdefault(
            row_complaint_key,
            {
                "complaint_key": row_complaint_key,
                "category_code": row["category_code"],
                "category_label": row["category_label"],
                "complaint_code": row["complaint_code"],
                "complaint_label": row["complaint_label"],
                "canonical_path": complaint_path,
                "details": [],
            },
        )
        complaint["details"].append(detail)

        category = categories.setdefault(
            row["category_code"],
            {
                "category_code": row["category_code"],
                "category_label": row["category_label"],
                "complaints": [],
            },
        )
        if complaint not in category["complaints"]:
            category["complaints"].append(complaint)

        criterion_key = (
            f"{row['detail_code']}|{row['detail_label']}|{row['ktas']}"
        )
        criterion_index.setdefault(criterion_key, []).append(
            {
                "detail_key": row_detail_key,
                "row_code": row["row_code"],
                "canonical_path": canonical_path,
            }
        )
        complaint_labels.setdefault(row["complaint_label"], {})[
            row_complaint_key
        ] = {
            "complaint_key": row_complaint_key,
            "canonical_path": complaint_path,
        }
        detail_labels.setdefault(row["detail_label"], {})[row_detail_key] = {
            "detail_key": row_detail_key,
            "row_code": row["row_code"],
            "canonical_path": canonical_path,
        }

    category_list = [categories[key] for key in sorted(categories)]
    complaint_list = [complaints[key] for key in sorted(complaints)]
    detail_list = sorted(details, key=lambda item: (item["detail_key"], item["row_code"]))

    category_index = [
        {
            "category_code": category["category_code"],
            "category_label": category["category_label"],
            "complaint_count": len(category["complaints"]),
            "routing_text": join_text(
                [
                    category["category_label"],
                    *(item["complaint_label"] for item in category["complaints"]),
                ]
            ),
        }
        for category in category_list
    ]
    complaint_index = []
    for complaint in complaint_list:
        enrichment = aliases.get(complaint["complaint_key"], {})
        canonical_terms = list(enrichment.get("canonical_terms", []))
        complaint_aliases = list(enrichment.get("aliases", []))
        complaint_index.append(
            {
                **{key: value for key, value in complaint.items() if key != "details"},
                "canonical_terms": canonical_terms,
                "aliases": complaint_aliases,
                "detail_count": len(complaint["details"]),
                "routing_text": join_text(
                    [
                        complaint["category_label"],
                        complaint["complaint_label"],
                        *canonical_terms,
                        *complaint_aliases,
                    ]
                ),
            }
        )

    complaint_collision_index = {
        label: [items[key] for key in sorted(items)]
        for label, items in sorted(complaint_labels.items())
        if len(items) > 1
    }
    detail_collision_index = {
        label: [items[key] for key in sorted(items)]
        for label, items in sorted(detail_labels.items())
        if len(items) > 1
    }

    return {
        "version": 1,
        "schema": {
            "source_columns": list(FIELD_NAMES),
            "complaint_key": "{category_code}:{complaint_code}",
            "detail_key": "{category_code}:{complaint_code}:{detail_code}",
            "criterion_key": "{detail_code}|{detail_label}|{ktas}",
            "evidence_primary_identifier": "row_code",
        },
        "stats": {
            "category_count": len(category_list),
            "complaint_count": len(complaint_list),
            "detail_row_count": len(detail_list),
            "unique_criterion_count": len(criterion_index),
        },
        "categories": category_list,
        "category_index": category_index,
        "complaint_index": complaint_index,
        "detail_index": detail_list,
        "criterion_index": {
            key: criterion_index[key] for key in sorted(criterion_index)
        },
        "complaint_label_collision_index": complaint_collision_index,
        "detail_label_collision_index": detail_collision_index,
    }
