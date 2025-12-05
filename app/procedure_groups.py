# app/procedure_groups.py
from __future__ import annotations

from typing import Dict, List, TypedDict, Optional
from datetime import datetime

from app.schemas import (
    HospitalSummary,
    ProcedureAvailability,
    HospitalMessage,
)


def _parse_block_dt(value: Optional[str]) -> Optional[datetime]:
    """
    symBlkSttDtm / symBlkEndDtm 문자열(YYYYMMDDHHMMSS 등)을 datetime으로 변환.
    실패하면 None.
    """
    if not value:
        return None
    s = str(value).strip()
    if not s:
        return None

    for fmt in ("%Y%m%d%H%M%S", "%Y-%m-%d%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _is_blocking_message(msg: HospitalMessage, now: Optional[datetime] = None) -> bool:
    """
    getEmrrmSrsillDissMsgInqire 응답에서
    - out_display_status(symOutDspYon)이 'N' 또는 '차단'인 경우
    - block_start ~ block_end 구간에 now가 포함되면 '차단'으로 본다.
    """
    status = (msg.out_display_status or "").strip()
    if not status:
        return False

    upper = status.upper()
    # N 또는 한글 '차단'이 있으면 차단 플래그로 본다.
    is_block_flag = upper.startswith("N") or ("차단" in status)
    if not is_block_flag:
        return False

    if now is None:
        now = datetime.now()

    start = _parse_block_dt(msg.block_start)
    end = _parse_block_dt(msg.block_end)

    # 기간 정보가 전혀 없으면: 일단 차단으로 본다(보수적으로)
    if start is None and end is None:
        return True

    if start is not None and end is not None:
        return start <= now <= end
    if start is not None:
        return now >= start
    # end만 있는 경우
    return now <= end


class ProcedureGroup(TypedDict):
    label: str                  # 화면용 이름
    serious_keys: List[str]     # SeriousDiseaseStatus.mkiosk 에서 보는 키들
    basic_keys: List[str]       # HospitalBasicInfo.raw_fields 의 MKioskTyXX 키들
    message_codes: List[str]    # HospitalMessage.message_type_code (Y코드)
    bed_types: List[str]        # 병상정보


# 매핑 Logic
# 중증수용정보 + 기본정보 MKioskTy 일원화
PROCEDURE_GROUPS: Dict[str, ProcedureGroup] = {
    # 1. 심근경색 (ACS / MI)
    "ACS_MI": {
        "label": "[심근경색] PCI/응급수술",
        "serious_keys": ["MKioskTy1"],
        "basic_keys": ["MKioskTy1"],
        "message_codes": ["Y0011", "Y0012"],
        # 🔹 응급실 + 성인 일반 ICU (내과/CCU 포함) 기준
        "bed_types": ["er", "icu_general"],
    },

    # 2. 뇌경색 재관류 / 뇌혈관중재
    "ACS_STROKE": {
        "label": "[뇌경색] 재관류/중재시술",
        "serious_keys": ["MKioskTy2"],
        "basic_keys": ["MKioskTy2"],
        "message_codes": ["Y0021", "Y0022"],
        # 응급실 + 신경계 ICU 묶음
        "bed_types": ["er", "icu_neuro"],
    },

    # 3. 뇌출혈 수술
    "BRAIN_HEMORRHAGE": {
        "label": "[뇌출혈] 개두/혈종제거",
        "serious_keys": ["MKioskTy3"],
        "basic_keys": ["MKioskTy3"],
        "message_codes": ["Y0031", "Y0032"],
        # 응급실 + 신경외과 ICU(hv6) 위주
        "bed_types": ["er", "icu_neurosurg"],
    },

    # 4. 대동맥응급
    "AORTIC_EMERGENCY": {
        "label": "[대동맥응급] 박리/파열",
        "serious_keys": ["MKioskTy4"],
        "basic_keys": ["MKioskTy4"],
        "message_codes": ["Y0041", "Y0042"],
        # 응급실 + 성인 일반 ICU (흉부외과계)
        "bed_types": ["er", "icu_general"],
    },

    # 5. 복부 응급수술 (담낭/장천공 등)
    "ABDOMINAL_EMERGENCY": {
        "label": "[복부응급] 담낭/장천공/복막염",
        "serious_keys": ["MKioskTy7", "MKioskTy8", "MKioskTy9"],
        "basic_keys": ["MKioskTy7", "MKioskTy8", "MKioskTy9"],
        "message_codes": ["Y0051", "Y0052"],
        # 응급실 + 수술실 + 일반 ICU (복부외과)
        "bed_types": ["er", "or", "icu_general"],
    },

    # 6. 장중첩/장폐색 (소아 포함)
    "INTUSSUSCEPTION": {
        "label": "[장중첩/폐색]",
        "serious_keys": ["MKioskTy10"],
        "basic_keys": ["MKioskTy10"],
        "message_codes": ["Y0061", "Y0062"],
        "bed_types": ["er"],
    },

    # 7. GI 내시경 (출혈 포함)
    "GI_ENDOSCOPY": {
        "label": "[위장관내시경] GI bleeding 포함",
        "serious_keys": ["MKioskTy11", "MKioskTy12"],
        "basic_keys": ["MKioskTy11", "MKioskTy12"],
        "message_codes": ["Y0071", "Y0072"],
        "bed_types": ["er"],
    },

    # 8. 기관지 내시경
    "BRONCHOSCOPY": {
        "label": "[기관지내시경]",
        "serious_keys": ["MKioskTy13", "MKioskTy14"],
        "basic_keys": ["MKioskTy13", "MKioskTy14"],
        "message_codes": ["Y0081", "Y0082"],
        # 🔹 중증 호흡부전 고려해서 ER + ICU general
        "bed_types": ["er", "icu_general"],
    },

    # 9. 사지접합
    "LIMB_REPLANTATION": {
        "label": "[사지접합]",
        "serious_keys": ["MKioskTy20", "MKioskTy21"],
        "basic_keys": ["MKioskTy20", "MKioskTy21"],
        "message_codes": ["Y0091", "Y0092"],
        # 응급실 + 수술실 + 일반 ICU (정형외과/수부외과)
        "bed_types": ["er", "or", "icu_general"],
    },

    # 10. 중증화상
    "SEVERE_BURN": {
        "label": "[중증화상]",
        "serious_keys": ["MKioskTy19"],
        "basic_keys": ["MKioskTy19"],
        "message_codes": ["Y0101", "Y0102"],
        # 응급실 + 화상 중환자실(hv8 / icu_burn) 명시
        "bed_types": ["er", "icu_burn"],
    },

    # 11. 산부인과 응급 (분만/산과수술)
    "OB_EMERGENCY": {
        "label": "[산부인과응급] 분만/산과수술",
        "serious_keys": ["MKioskTy16", "MKioskTy17", "MKioskTy18"],
        "basic_keys": ["MKioskTy16", "MKioskTy17", "MKioskTy18"],
        "message_codes": ["Y0111", "Y0112"],
        "bed_types": ["er", "or"],
    },

    # 12. 저체중 출생아 / 신생아 집중치료
    "NEONATE_LBW": {
        "label": "[저체중출생아] 신생아집중치료",
        "serious_keys": ["MKioskTy15"],
        "basic_keys": ["MKioskTy15"],
        "message_codes": ["Y0121", "Y0122"],
        "bed_types": ["icu_neonatal"],
    },

    # 13. 응급투석
    "EMERGENCY_DIALYSIS": {
        "label": "[응급투석] HD/CRRT",
        "serious_keys": ["MKioskTy22", "MKioskTy23"],
        "basic_keys": ["MKioskTy22", "MKioskTy23"],
        "message_codes": ["Y0141", "Y0142"],
        "bed_types": ["er"],
    },

    # 14. 정신과적 응급
    "PSYCHIATRIC_EMERGENCY": {
        "label": "[정신과적응급] 폐쇄병동입원",
        "serious_keys": ["MKioskTy24"],
        "basic_keys": ["MKioskTy24"],
        "message_codes": ["Y0151", "Y0152"],
        "bed_types": ["ward_psych"],
    },

    # 15. 영상의학 중재 (혈관중재)
    "IR_INTERVENTION": {
        "label": "[혈관중재] 영상의학",
        "serious_keys": ["MKioskTy26", "MKioskTy27"],
        "basic_keys": ["MKioskTy26", "MKioskTy27"],
        "message_codes": ["Y0161", "Y0162"],
        "bed_types": ["er", "icu_general"],
    },

    # 16. 안과 응급수술
    "EYE_EMERGENCY": {
        "label": "[안과응급] 안구손상/출혈",
        "serious_keys": ["MKioskTy25"],
        "basic_keys": ["MKioskTy25"],
        "message_codes": ["Y0171", "Y0172"],
        "bed_types": ["er"],
    },
}


def _normalize_flag(value: Optional[str]) -> Optional[str]:
    """MKioskTy 값(Y / N / N1 / 불가능 / 정보미제공)을 요약 상태로 통일."""
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return None

    # 문서 기준: Y=가능, 그 외 코드 (N, N1 등)는 거의 다 불가능/미제공 의미
    if v.upper().startswith("Y"):
        return "가능"
    if "불가" in v or "불가능" in v:
        return "불가능"
    if v.upper().startswith("N"):
        # N, N1 등은 일단 '불가능' 쪽으로 보는 게 안전
        return "불가능"
    if v == "정보미제공":
        return "정보미제공"
    # 그 밖의 애매한 값은 일단 정보미제공 처리
    return "정보미제공"


def compute_procedure_availability(
    summary: HospitalSummary,
) -> Dict[str, ProcedureAvailability]:
    """
    한 병원의 HospitalSummary를 받아서
    PROCEDURE_GROUPS 기준으로 수술 가능 여부를 정리.
    """

    serious = summary.serious
    basic = summary.basic
    messages = summary.messages or []

    result: Dict[str, ProcedureAvailability] = {}

    for group_id, cfg in PROCEDURE_GROUPS.items():
        serious_vals: List[str] = []
        basic_vals: List[str] = []

        # 1) 중증 수용 API에서 우선 확인
        if serious and serious.mkiosk:
            for key in cfg["serious_keys"]:
                if key in serious.mkiosk:
                    serious_vals.append(serious.mkiosk.get(key))

        # 2) 기본정보 MKioskTy로 보강
        if basic and basic.raw_fields:
            for key in cfg["basic_keys"]:
                if key in basic.raw_fields:
                    basic_vals.append(basic.raw_fields.get(key))

        serious_statuses = [
            _normalize_flag(v) for v in serious_vals if v is not None
        ]
        basic_statuses = [
            _normalize_flag(v) for v in basic_vals if v is not None
        ]

        status: str
        source: str = "none"

        # 우선순위: serious → basic → none
        if serious_statuses:
            if "가능" in serious_statuses:
                status = "가능"
            elif "불가능" in serious_statuses:
                status = "불가능"
            else:
                status = "정보미제공"
            source = "serious"
        elif basic_statuses:
            if "가능" in basic_statuses:
                status = "가능"
            elif "불가능" in basic_statuses:
                status = "불가능"
            else:
                status = "정보미제공"
            source = "basic"
        else:
            status = "정보미제공"
            source = "none"

        # 3) 메시지(Y코드) 기반 override
        #   - message_type == "중증"
        #   - message_type_code 가 이 procedure group의 message_codes 중 하나
        #   - symOutDspYon == 'N'(또는 '차단') 이고, block_start~block_end 구간 안이면 "불가능"
        #   - (보너스) 메시지 텍스트에 "불가/불가능"이 있으면 역시 "불가능"
        if messages:
            now = datetime.now()
            related_msgs = [
                m
                for m in messages
                if m.message_type == "중증"
                and m.message_type_code in cfg["message_codes"]
            ]

            for m in related_msgs:
                # 1) 정식 차단 플래그 + 시간 구간 기준
                if _is_blocking_message(m, now=now):
                    status = "불가능"
                    source = f"{source}+message"
                    break

                # 2) out_display_status가 애매해도, 텍스트에 '불가/불가능' 있으면 보수적으로 차단
                msg_text = (m.message or "")
                if "불가" in msg_text or "불가능" in msg_text:
                    status = "불가능"
                    source = f"{source}+message"
                    break

        result[group_id] = ProcedureAvailability(
            label=cfg["label"],
            status=status,
            source=source,
        )

    return result

PROCEDURE_GROUP_LABELS: dict[str, str] = {
    # 1. 심근경색 (ACS / MI)
    "ACS_MI": "심근경색/ACS (응급 PCI)",

    # 2. 뇌경색 재관류 / 뇌혈관중재
    "ACS_STROKE": "뇌졸중 (재관류/중재)",

    # 3. 뇌출혈 수술
    "BRAIN_HEMORRHAGE": "뇌출혈 수술",

    # 4. 대동맥응급
    "AORTIC_EMERGENCY": "대동맥 응급(박리/파열)",

    # 5. 복부 응급수술 (담낭/장천공 등)
    "ABDOMINAL_EMERGENCY": "복부 응급수술",

    # 6. 장중첩/장폐색 (소아 포함)
    "INTUSSUSCEPTION": "장중첩/장폐색",

    # 7. GI 내시경 (출혈 포함)
    "GI_ENDOSCOPY": "소화기 내시경(출혈 포함)",

    # 8. 기관지 내시경
    "BRONCHOSCOPY": "기관지 내시경",

    # 9. 사지접합
    "LIMB_REPLANTATION": "사지접합 수술",

    # 10. 중증화상
    "SEVERE_BURN": "중증 화상 치료",

    # 11. 산부인과 응급 (분만/산과수술)
    "OB_EMERGENCY": "산부인과 응급(분만/수술)",

    # 12. 저체중 출생아 / 신생아 집중치료
    "NEONATE_LBW": "저체중 출생아/신생아 집중치료",

    # 13. 응급투석
    "EMERGENCY_DIALYSIS": "응급투석(HD/CRRT)",

    # 14. 정신과적 응급
    "PSYCHIATRIC_EMERGENCY": "정신과적 응급/폐쇄병동",

    # 15. 영상의학 중재 (혈관중재)
    "IR_INTERVENTION": "혈관중재(영상의학)",

    # 16. 안과 응급수술
    "EYE_EMERGENCY": "안과 응급수술",
}

def humanize_procedure_groups(group_ids: list[str]) -> list[str]:
    """코드 리스트를 사람이 읽을 수 있는 한글 라벨 리스트로 변환."""
    return [PROCEDURE_GROUP_LABELS.get(gid, gid) for gid in group_ids]