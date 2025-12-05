# app/services/ermct_client.py
from __future__ import annotations

from typing import List, Any, Dict, Optional

import requests
import xmltodict

from app.config import ERMCT_SERVICE_KEY
from app.schemas import (
    HospitalRealtime,
    HospitalBasicInfo,
    SeriousDiseaseStatus,
    HospitalMessage,
    TraumaCenter,
)

BASE_URL = "http://apis.data.go.kr/B552657/ErmctInfoInqireService"

class ErmctClient:
    def __init__(self, service_key: str | None = None, timeout: int = 5) -> None:
        self.service_key = service_key or ERMCT_SERVICE_KEY
        self.timeout = timeout

    # ---------- 공통 변환 헬퍼 ----------

    def _to_int(self, x: Any) -> Optional[int]:
        if x is None:
            return None
        s = str(x).strip()
        if not s:
            return None
        try:
            return int(s)
        except Exception:
            return None

    def _to_float(self, x: Any) -> Optional[float]:
        if x is None:
            return None
        s = str(x).strip()
        if not s:
            return None
        try:
            return float(s)
        except Exception:
            return None

    # ---------- 공통 GET 래퍼 ----------

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query = {
            "serviceKey": self.service_key,
            **params,
        }
        url = f"{BASE_URL}/{path}"
        resp = requests.get(url, params=query, timeout=self.timeout)
        resp.raise_for_status()

        data = xmltodict.parse(resp.text)
        response = data.get("response", {})
        header = response.get("header", {})

        result_code = header.get("resultCode")
        if result_code != "00":
            msg = header.get("resultMsg", "Unknown error")
            raise RuntimeError(f"API error {result_code}: {msg}")

        body = response.get("body") or {}
        return body

    #  ---------- 1. 실시간 병상 조회  ----------

    def get_realtime_beds(
        self,
        sido: str,
        sigungu: str,
        num_rows: int = 50,
        page_no: int = 1,
    ) -> List[HospitalRealtime]:
        """
        응급실 실시간 가용 병상 정보 조회
        (getEmrrmRltmUsefulSckbdInfoInqire)
        """
        body = self._get(
            "getEmrrmRltmUsefulSckbdInfoInqire",
            {
                "STAGE1": sido,
                "STAGE2": sigungu,
                "numOfRows": num_rows,
                "pageNo": page_no,
            },
        )

        if not isinstance(body, dict):
            return []

        items_container = body.get("items")
        if not items_container:
            # 해당 시군구에 응급의료기관이 없거나, 일시적으로 데이터가 없을 때
            return []

        items = items_container.get("item", [])
        if not items:
            return []

        # item이 하나일 때 dict로 들어오는 경우를 대비
        if isinstance(items, dict):
            items = [items]

        def to_int(x: Any) -> Optional[int]:
            if x is None:
                return None
            s = str(x).strip()
            if not s:
                return None
            try:
                return int(s)
            except Exception:
                return None

        def to_bool(x: Any) -> Optional[bool]:
            if x is None:
                return None
            s = str(x).strip().upper()
            # 공공데이터에서 N1 같은 꼴도 나와서 묶어서 처리
            if s in {"Y", "YES", "1"}:
                return True
            if s in {"N", "N0", "N1", "0"}:
                return False
            return None

        results: List[HospitalRealtime] = []

        for it in items:
            # 1) 원본 태그 전체 백업 (문자열 기반)
            raw_fields: Dict[str, Any] = {}
            for k, v in it.items():
                if v is None:
                    raw_fields[k] = None
                else:
                    raw_fields[k] = str(v)

            # 2) 숫자 hvXX / hvsXX만 따로 파싱
            raw_hv: Dict[str, Optional[int]] = {}
            baseline_hvs: Dict[str, Optional[int]] = {}

            for k, v in it.items():
                key_lower = k.lower()

                # hv + 숫자 (예: hv28, hv29, hv30, hv41, hv6 ...)
                # hv10/hv11/hv5/hv7/hv42 같은 Y/N 필드는 int 변환 실패 → None
                # → 그런 값들은 raw_hv에 넣지 않는다 (숫자만 보관)
                if key_lower.startswith("hv") and len(key_lower) > 2 and key_lower[2].isdigit() and not key_lower.startswith("hvs"):
                    iv = to_int(v)
                    if iv is not None:
                        raw_hv[key_lower] = iv

                # hvs + 숫자 (기준 병상)
                if key_lower.startswith("hvs") and len(key_lower) > 3 and key_lower[3].isdigit():
                    iv = to_int(v)
                    if iv is not None:
                        baseline_hvs[key_lower] = iv

            # 3) 자주 쓰는 필드는 명시적 스키마 필드로 매핑
            name = it.get("dutyName") or it.get("dutyname")
            phone = it.get("dutyTel3") or it.get("dutytel3")

            hospital = HospitalRealtime(
                id=str(it.get("hpid")),
                name=str(name) if name is not None else "",
                phone=phone,

                rnum=to_int(it.get("rnum")),
                old_id=it.get("phpid"),
                input_datetime=it.get("hvidate"),

                # 병상 요약
                er_beds=to_int(it.get("hvec")),
                or_beds=to_int(it.get("hvoc")),
                neuro_icu_beds=to_int(it.get("hvcc")),
                neonatal_icu_beds=to_int(it.get("hvncc")),
                thoracic_icu_beds=to_int(it.get("hvccc")),
                general_icu_beds=to_int(it.get("hvicc")),
                ward_beds=to_int(it.get("hvgc")),

                # 장비/자원 가용 여부
                ct_available=to_bool(it.get("hvctayn")),
                mri_available=to_bool(it.get("hvmriayn")),
                angio_available=to_bool(it.get("hvangioayn")),
                ventilator_available=to_bool(it.get("hvventiayn")),
                ventilator_premature_available=to_bool(it.get("hvventisoayn")),
                incubator_available=to_bool(it.get("hvincuayn")),
                crrt_available=to_bool(it.get("hvcrrtayn")),
                ecmo_available=to_bool(it.get("hvecmoayn")),
                hyperbaric_oxygen_available=to_bool(it.get("hvoxyayn")),
                hypothermia_available=to_bool(it.get("hvhypoayn")),
                ambulance_available=to_bool(it.get("hvamyn")),

                # 소아/특수 플래그
                pediatric_ventilator_flag=to_bool(it.get("hv10")),
                incubator_flag=to_bool(it.get("hv11")),
                neuro_ward_flag=to_bool(it.get("hv5")),
                toxic_icu_flag=to_bool(it.get("hv7")),
                pediatric_icu_flag=to_bool(it.get("hv42")),

                raw_hv=raw_hv,
                baseline_hvs=baseline_hvs,
                raw_fields=raw_fields,
            )

            results.append(hospital)

        return results

    # ---------- 2. 기본정보 조회 (getEgytBassInfoInqire) ----------

    def get_basic_info(
        self,
        hpid: str,
        num_rows: int = 1,
        page_no: int = 1,
    ) -> Optional[HospitalBasicInfo]:
        """
        응급의료기관 기본정보 조회
        (getEgytBassInfoInqire)
        HPID 기준으로 병원 기본정보(주소, 전화, 위경도 등)를 가져온다.
        """
        body = self._get(
            "getEgytBassInfoInqire",
            {
                "HPID": hpid,
                "pageNo": page_no,
                "numOfRows": num_rows,
            },
        )

        items = body.get("items", {}).get("item")
        if not items:
            return None

        # item 이 리스트일 수도, dict 일 수도 있어서 통일
        if isinstance(items, list):
            it = items[0]
        else:
            it = items

        # 문자열은 일단 strip 해두자
        clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in it.items()}

        return HospitalBasicInfo(
            id=clean.get("hpid") or clean.get("emcOrgCod") or hpid,
            name=clean.get("dutyName"),
            address=clean.get("dutyAddr"),
            phone=clean.get("dutyTel1") or clean.get("dutyTel2"),
            emergency_phone=clean.get("dutyTel3"),
            latitude=self._to_float(clean.get("wgs84Lat") or clean.get("latitude")),
            longitude=self._to_float(clean.get("wgs84Lon") or clean.get("longitude")),
            start_time=clean.get("startTime"),
            end_time=clean.get("endTime"),
            rnum=self._to_int(clean.get("rnum")),
            raw_fields=clean,
        )

    # ---------- 3. 중증질환 수용가능 정보 (getSrsillDissAceptncPosblInfoInqire) ----------

    def get_serious_acceptance(
        self,
        sido: str,
        sigungu: str,
        sm_type: int = 1,
        num_rows: int = 30,
        page_no: int = 1,
    ) -> List[SeriousDiseaseStatus]:
        """
        중증질환자 수용가능정보 조회
        (getSrsillDissAceptncPosblInfoInqire)

        - STAGE1: 시도
        - STAGE2: 시군구
        - SM_TYPE: 1/2/3 등 (가이드 문서 기준)
        """
        body = self._get(
            "getSrsillDissAceptncPosblInfoInqire",
            {
                "STAGE1": sido,
                "STAGE2": sigungu,
                "SM_TYPE": sm_type,
                "pageNo": page_no,
                "numOfRows": num_rows,
            },
        )

        if not isinstance(body, dict):
            return []

        items_container = body.get("items")
        if not items_container:
            # 데이터 없을 때
            return []

        items = items_container.get("item", [])
        if not items:
            return []

        if isinstance(items, dict):
            items = [items]

        results: List[SeriousDiseaseStatus] = []

        for it in items:
            clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in it.items()}

            mkiosk: Dict[str, Optional[str]] = {}
            mkiosk_msg: Dict[str, Optional[str]] = {}
            others: Dict[str, Any] = {}

            for k, v in clean.items():
                if k.startswith("MKioskTy") and k.endswith("Msg"):
                    mkiosk_msg[k] = v
                elif k.startswith("MKioskTy"):
                    mkiosk[k] = v
                else:
                    others[k] = v

            results.append(
                SeriousDiseaseStatus(
                    name=clean.get("dutyName"),
                    mkiosk=mkiosk,
                    mkiosk_msg=mkiosk_msg,
                    raw_fields=others,
                )
            )

        return results

    # ---------- 4. 응급실/중증 메시지 (getEmrrmSrsillDissMsgInqire) ----------

    def get_emergency_messages(
        self,
        hpid: str,
        num_rows: int = 10,
        page_no: int = 1,
    ) -> List[HospitalMessage]:
        """
        응급실 및 중증질환 메시지 조회
        (getEmrrmSrsillDissMsgInqire)

        HPID 기준으로 최근 메시지를 가져온다.
        """
        body = self._get(
            "getEmrrmSrsillDissMsgInqire",
            {
                "HPID": hpid,
                "pageNo": page_no,
                "numOfRows": num_rows,
            },
        )

        # body None / 비 dict 방어
        if not isinstance(body, dict):
            return []

        items_container = body.get("items")
        if not items_container:
            # 해당 병원에 메시지가 없거나, 일시적으로 데이터 없음
            return []

        items = items_container.get("item", [])
        if not items:
            return []

        if isinstance(items, dict):
            items = [items]

        results: List[HospitalMessage] = []

        for it in items:
            clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in it.items()}

            results.append(
                HospitalMessage(
                    id=clean.get("hpid") or hpid,
                    name=clean.get("dutyName"),
                    address=clean.get("dutyAddr"),
                    emc_org_code=clean.get("emcOrgCod"),
                    rnum=self._to_int(clean.get("rnum")),
                    message=clean.get("symBlkMsg"),
                    message_type=clean.get("symBlkMsgTyp"),
                    message_type_code=clean.get("symTypCod"),
                    message_type_name=clean.get("symTypCodMag"),
                    out_display_method=clean.get("symOutDspMth"),
                    out_display_status=clean.get("symOutDspYon"),
                    block_start=clean.get("symBlkSttDtm"),
                    block_end=clean.get("symBlkEndDtm"),
                    raw_fields=clean,
                )
            )

        return results



    def debug_raw_serious_xml(self, sido: str, sigungu: str, sm_type: int = 1,
                            num_rows: int = 30, page_no: int = 1) -> str:
        url = f"{BASE_URL}/getSrsillDissAceptncPosblInfoInqire"
        query = {
            "serviceKey": self.service_key,
            "STAGE1": sido,
            "STAGE2": sigungu,
            "SM_TYPE": sm_type,
            "pageNo": page_no,
            "numOfRows": num_rows,
        }
        resp = requests.get(url, params=query, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
    

    def get_trauma_centers(
        self,
        sido: str,
        sigungu: str,
        num_rows: int = 50,
        page_no: int = 1,
    ) -> List[TraumaCenter]:
        """
        외상센터 목록정보 조회
        (getStrmListInfoInqire)
        """
        body = self._get(
            "getStrmListInfoInqire",
            {
                "Q0": sido,
                "Q1": sigungu,
                "QZ": "A",          # 기관분류(응급의료기관) – 가이드 기본 예시값
                "ORD": "ADDR",     # 주소순
                "pageNo": page_no,
                "numOfRows": num_rows,
            },
        )

        if not isinstance(body, dict):
            return []

        items_container = body.get("items")
        if not items_container:
            return []

        items = items_container.get("item", [])
        if not items:
            return []

        if isinstance(items, dict):
            items = [items]

        results: List[TraumaCenter] = []
        for it in items:
            clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in it.items()}

            tc = TraumaCenter(
                id=str(clean.get("hpid")),
                name=clean.get("dutyName"),
                address=clean.get("dutyAddr"),
                emc_class_code=clean.get("dutyEmcls"),
                emc_class_name=clean.get("dutyEmclsName"),
                tel=clean.get("dutyTel1"),
                er_tel=clean.get("dutyTel3"),
                lat=self._to_float(clean.get("wgs84Lat")),
                lon=self._to_float(clean.get("wgs84Lon")),
                raw_fields=clean,
            )
            results.append(tc)

        return results