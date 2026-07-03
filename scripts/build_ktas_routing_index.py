from __future__ import annotations

import csv
from pathlib import Path
from typing import TypedDict


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
