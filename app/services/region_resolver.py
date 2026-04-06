from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import requests

from app.config import KAKAO_REST_API_KEY
from app.services.sigungu_search import ResolvedSigungu


KAKAO_COORD2REGION_URL = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json"


@dataclass(frozen=True)
class KakaoRegion:
    sido_name: str
    sigungu_name: str
    dong_name: Optional[str] = None


def _strip_region_suffix(name: str) -> str:
    return name.strip().replace("특별자치", "").replace("특별", "")


def _extract_kakao_region(data: dict[str, Any]) -> Optional[KakaoRegion]:
    documents = data.get("documents")
    if not isinstance(documents, list):
        return None

    candidates = [
        item for item in documents
        if isinstance(item, dict) and item.get("region_type") == "B"
    ] or [
        item for item in documents if isinstance(item, dict)
    ]

    if not candidates:
        return None

    item = candidates[0]
    sido_name = str(item.get("region_1depth_name") or "").strip()
    sigungu_name = str(item.get("region_2depth_name") or "").strip()
    dong_name = str(item.get("region_3depth_name") or "").strip() or None

    if not sido_name or not sigungu_name:
        return None

    return KakaoRegion(
        sido_name=sido_name,
        sigungu_name=sigungu_name,
        dong_name=dong_name,
    )


class KakaoRegionResolver:
    def __init__(self, api_key: str | None = None, timeout: float = 2.5) -> None:
        self.api_key = api_key or KAKAO_REST_API_KEY
        self.timeout = timeout

    def resolve_region(self, lat: float, lon: float) -> Optional[KakaoRegion]:
        if not self.api_key:
            return None

        headers = {"Authorization": f"KakaoAK {self.api_key}"}
        params = {
            "x": lon,
            "y": lat,
            "input_coord": "WGS84",
        }

        response = requests.get(
            KAKAO_COORD2REGION_URL,
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return _extract_kakao_region(data)

    def resolve_sigungu(self, lat: float, lon: float) -> Optional[ResolvedSigungu]:
        region = self.resolve_region(lat, lon)
        if not region:
            return None

        return ResolvedSigungu(
            sigungu_code="",
            sigungu_name=_strip_region_suffix(region.sigungu_name),
            sido_code=None,
            sido_name=region.sido_name,
        )
