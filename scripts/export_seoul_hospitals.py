# scripts/export_seoul_hospitals.py
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Set, List

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

# mkioskty 코드 → 응급수술/중증질환 한글 레이블
MKIOSK_LABELS: Dict[str, str] = {
    "MKioskTy1":  "[재관류중재술] 심근경색",
    "MKioskTy2":  "[재관류중재술] 뇌경색",
    "MKioskTy3":  "[뇌출혈수술] 거미막하출혈",
    "MKioskTy4":  "[뇌출혈수술] 거미막하출혈 외",
    "MKioskTy5":  "[대동맥응급] 흉부",
    "MKioskTy6":  "[대동맥응급] 복부",
    "MKioskTy7":  "[담낭담관질환] 담낭질환",
    "MKioskTy8":  "[담낭담관질환] 담도포함질환",
    "MKioskTy9":  "[복부응급수술] 비외상",
    "MKioskTy10": "[장중첩/폐색] 영유아",
    "MKioskTy11": "[응급내시경] 성인 위장관",
    "MKioskTy12": "[응급내시경] 영유아 위장관",
    "MKioskTy13": "[응급내시경] 성인 기관지",
    "MKioskTy14": "[응급내시경] 영유아 기관지",
    "MKioskTy15": "[저체중출생아] 집중치료",
    "MKioskTy16": "[산부인과응급] 분만",
    "MKioskTy17": "[산부인과응급] 산과수술",
    "MKioskTy18": "[산부인과응급] 부인과수술",
    "MKioskTy19": "[중증화상] 전문치료",
    "MKioskTy20": "[사지접합] 수족지접합",
    "MKioskTy21": "[사지접합] 수족지접합 외",
    "MKioskTy22": "[응급투석] HD",
    "MKioskTy23": "[응급투석] CRRT",
    "MKioskTy24": "[정신과적응급] 폐쇄병동입원",
    "MKioskTy25": "[안과적수술] 응급",
    "MKioskTy26": "[영상의학혈관중재] 성인",
    "MKioskTy27": "[영상의학혈관중재] 소아",
    "MKioskTy28": "응급실(Emergency gate keeper)",
}


def normalize_flag(x: str | None) -> str:
    """
    mkiosk 값 정규화: Y / N / 정보미제공 / 기타
    """
    if x is None:
        return ""
    s = str(x).strip()
    if not s:
        return ""
    # 공공데이터에서 N, 불가능, N1 등 섞여 있을 수 있어서 대충 그룹화
    if s.upper() == "Y":
        return "Y"
    if s.upper().startswith("N") or "불가" in s or "불가능" in s:
        return "N"
    if "정보미제공" in s:
        return "정보미제공"
    return s  # 그 외는 그대로


def main() -> None:
    client = ErmctClient()

    # 1) 실시간 병상 기준 서울 병원 목록 수집
    seen: Set[str] = set()
    base_rows: list[Dict[str, str]] = []

    # 2) 중증질환 수용가능 정보(hpid → mkiosk dict)도 같이 모으기
    serious_by_hpid: Dict[str, Dict[str, str]] = {}

    for gu in SEOUL_SIGUNGU_LIST:
        print(f"[INFO] {gu} 병원 조회 중...")

        # (1) 실시간 병상 정보
        hospitals = client.get_realtime_beds(
            sido="서울특별시",
            sigungu=gu,
            num_rows=200,
        )

        # (2) 중증질환 수용가능 정보
        #    SM_TYPE=1 이 mkioskty1~28 전체에 대한 플래그.
        serious_list = client.get_serious_acceptance(
            sido="서울특별시",
            sigungu=gu,
            sm_type=1,
            num_rows=200,
        )

        for s in serious_list:
            hpid = s.raw_fields.get("hpid")
            if not hpid:
                continue
            # mkiosk는 {"MKioskTy1": "Y", ...} 꼴
            serious_by_hpid[hpid] = s.mkiosk

        for h in hospitals:
            if not h.id or h.id in seen:
                continue
            seen.add(h.id)

            base_rows.append(
                {
                    "id": h.id,
                    "name": h.name or "",
                    "sigungu": gu,
                }
            )

    # 3) 각 병원별로 가능한/불가능한 응급수술 요약 컬럼 생성
    rows_with_surgery: List[Dict[str, str]] = []

    for row in base_rows:
        hpid = row["id"]
        mkiosk = serious_by_hpid.get(hpid, {})

        available: list[str] = []
        unavailable: list[str] = []

        for key, label in MKIOSK_LABELS.items():
            flag_raw = mkiosk.get(key)
            flag = normalize_flag(flag_raw)

            if flag == "Y":
                available.append(label)
            elif flag == "N":
                unavailable.append(label)
            # "정보미제공" 이나 "" 는 둘 다에 넣지 않음

        row_out = {
            **row,
            "available_surgeries": ", ".join(available),
            "unavailable_surgeries": ", ".join(unavailable),
        }
        rows_with_surgery.append(row_out)

    # 4) CSV로 저장
    out_path = Path("seoul_hospitals_with_surgery.csv")
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "name",
                "sigungu",
                "available_surgeries",
                "unavailable_surgeries",
            ],
        )
        writer.writeheader()
        writer.writerows(rows_with_surgery)

    print(f"[DONE] {len(rows_with_surgery)}개 병원 저장 완료 → {out_path.resolve()}")


if __name__ == "__main__":
    main()
