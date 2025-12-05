# app/config_beds.py

from typing import Dict, Callable
from app.schemas import HospitalRealtime


def _safe_int(v) -> int:
    """None / 문자열 섞여도 안전하게 int로 변환."""
    if v is None:
        return 0
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


# -----------------------------
# 기본 요약 병상
# -----------------------------
def _er_beds(rt: HospitalRealtime) -> int:
    """
    응급실 병상.
    """
    if rt.er_beds is None:
        return 0
    return rt.er_beds


def _or_beds(rt: HospitalRealtime) -> int:
    """수술실 병상 (hvoc)."""
    return max(_safe_int(rt.or_beds), 0)


def _icu_general(rt: HospitalRealtime) -> int:
    """일반 ICU (hvicc)."""
    return max(_safe_int(rt.general_icu_beds), 0)


def _icu_neonatal(rt: HospitalRealtime) -> int:
    """신생아 ICU (hvncc → neonate_icu_beds)."""
    return max(_safe_int(rt.neonatal_icu_beds), 0)


def _ward_general(rt: HospitalRealtime) -> int:
    """일반 병동 (hvgc → ward_beds)."""
    return max(_safe_int(rt.ward_beds), 0)


# -----------------------------
# 세부 ICU / 병동 (hv* + HVS*)
# -----------------------------
def _icu_neuro_from_raw(rt: HospitalRealtime) -> int:
    """
    신경계 ICU 대략값.
    - 우선 요약 필드 neuro_icu_beds가 있으면 그걸 사용.
    - 없으면 hv6([중환자실] 신경외과) + hvs12(신경외과 ICU 기준)로 추정.
    """
    # 1) 스키마에 요약 필드가 있으면 그쪽 우선
    if rt.neuro_icu_beds is not None:
        return max(_safe_int(rt.neuro_icu_beds), 0)

    hv = _safe_int(rt.raw_hv.get("hv6"))
    cap = _safe_int(rt.baseline_hvs.get("hvs12"))  # [중환자실] 신경외과_기준

    if cap > 0 and hv > cap:
        hv = cap
    return max(hv, 0)


def _ward_psych(rt: HospitalRealtime) -> int:
    """
    정신과 폐쇄병동 병상.
    - hv40: [입원실] 정신과 폐쇄병동
    - hvs24: [입원실] 정신과 폐쇄병동_기준
    """
    hv = _safe_int(rt.raw_hv.get("hv40"))
    cap = _safe_int(rt.baseline_hvs.get("hvs24"))  # 기준 병상

    if cap > 0 and hv > cap:
        hv = cap
    return max(hv, 0)


# bed_type 이름 -> 실시간 가용병상 계산함수
BED_TYPE_FUNCS: Dict[str, Callable[[HospitalRealtime], int]] = {
    # 기본 요약 타입
    "er": _er_beds,
    "or": _or_beds,
    "icu_general": _icu_general,
    "icu_neonatal": _icu_neonatal,
    "ward": _ward_general,

    # 신경계 ICU: 둘 다 같은 함수에 매핑해서 key mismatch 방지
    "icu_neuro": _icu_neuro_from_raw,
    "icu_neurosurg": _icu_neuro_from_raw,

    # 정신과 폐쇄병동
    "ward_psych": _ward_psych,
}
