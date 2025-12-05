# scripts/export_seoul_hospitals_geo.py
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Set

from app.services.ermct_client import ErmctClient

# 서울특별시 25개 자치구
SEOUL_SIGUNGU_LIST = [
    "강남구",
    "강동구",
    "강북구",
    "강서구",
    "관악구",
    "광진구",
    "구로구",
    "금천구",
    "노원구",
    "도봉구",
    "동대문구",
    "동작구",
    "마포구",
    "서대문구",
    "서초구",
    "성동구",
    "성북구",
    "송파구",
    "양천구",
    "영등포구",
    "용산구",
    "은평구",
    "종로구",
    "중구",
    "중랑구",
]


def main() -> None:
    client = ErmctClient()
    seen: Set[str] = set()
    rows: list[Dict[str, str]] = []

    for gu in SEOUL_SIGUNGU_LIST:
        print(f"[INFO] {gu} 병원 조회 중...")
        hospitals = client.get_realtime_beds(
            sido="서울특별시",
            sigungu=gu,
            num_rows=200,
        )

        for h in hospitals:
            if not h.id:
                continue
            if h.id in seen:
                continue
            seen.add(h.id)

            # 기본정보에서 주소 / 위도 / 경도 가져오기
            basic = client.get_basic_info(h.id)
            if basic is None:
                print(f"[WARN] 기본정보 없음: hpid={h.id} ({h.name})")
            
            # 이름은 기본정보가 우선, 없으면 realtime 이름 사용
            name = (basic.name if basic and basic.name else h.name) or ""

            rows.append(
                {
                    "id": h.id,
                    "name": name,
                    "sigungu": gu,
                    "address": basic.address if basic and basic.address else "",
                    "phone": basic.phone if basic and basic.phone else "",
                    "emergency_phone": basic.emergency_phone if basic and basic.emergency_phone else "",
                    "latitude": (
                        str(basic.latitude)
                        if basic and basic.latitude is not None
                        else ""
                    ),
                    "longitude": (
                        str(basic.longitude)
                        if basic and basic.longitude is not None
                        else ""
                    ),
                }
            )

    out_path = Path("seoul_hospitals_geo.csv")
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "name",
                "sigungu",
                "address",
                "phone",
                "emergency_phone",
                "latitude",
                "longitude",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[DONE] {len(rows)}개 병원 저장 완료 → {out_path.resolve()}")


if __name__ == "__main__":
    main()
