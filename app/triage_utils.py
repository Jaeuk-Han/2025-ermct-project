# app/triage_utils.py
from typing import List, Dict, Tuple, Iterable

from app.schemas import HospitalSummary, HospitalRealtime
from app.config_beds import BED_TYPE_FUNCS
from app.procedure_groups import PROCEDURE_GROUPS, compute_procedure_availability
from app.state_assignments import pending_assignments

PRIMARY_BED_TYPE_PRIORITY = [
    "er",
    "icu_general",
    "icu_neuro",
    "icu_surg",
    "nicu",
    "ward_psychiatric",
    "ward",
    "or",
]


def choose_primary_bed_type(bed_types: Iterable[str]) -> str | None:
    """
    여러 bed_type 후보 중에서 '예약'에 사용할 대표 bed_type 하나 고르기.
    - er가 있으면 무조건 er
    - 없으면 우선순위대로 첫 번째
    - 그래도 없으면 None
    """
    bed_set = set(bed_types)
    if not bed_set:
        return None

    for bt in PRIMARY_BED_TYPE_PRIORITY:
        if bt in bed_set:
            return bt

    # 우선순위에 없는 타입만 있다면 그냥 하나 골라서 사용
    return next(iter(bed_set))


def _api_beds_for_bed_types(
    realtime: HospitalRealtime,
    bed_types: List[str],
) -> int:
    """
    주어진 bed_types에 대해,
    각 bed_type별 가용 병상 수를 계산하고 그 중 최소값을 api_beds로 사용.
    (어느 하나라도 0이면 전체가 0)
    """
    if not realtime:
        return 0

    capacities = []
    # 혹시 중복 들어와도 의미 없으니 set으로 한 번 정리
    for bt in set(bed_types):
        func = BED_TYPE_FUNCS.get(bt)
        if not func:
            continue
        # 음수 방지
        cap = max(func(realtime), 0)
        capacities.append(cap)

    if not capacities:
        return 0
    return min(capacities)


def get_effective_beds(
    hpid: str,
    realtime: HospitalRealtime,
    bed_types: List[str],
) -> Tuple[int, int]:
    """
    [그룹 단위] bed_types 중 가장 빡센 병상 기준으로,
    - api_beds    : 현재 API 상 가용 병상 수 (pending 미반영)
    - effective   : api_beds - pending_assignments 를 적용한 값
    을 튜플로 반환.
    """
    api_beds = _api_beds_for_bed_types(realtime, bed_types)
    if api_beds <= 0:
        return 0, 0

    # 해당 병원에서 이 bed_types들을 사용하는 pending 환자 수 합산
    pending_total = 0
    for bt in set(bed_types):
        pending_total += pending_assignments[hpid][bt]

    effective_beds = max(api_beds - pending_total, 0)
    return api_beds, effective_beds


#   새로운 helper: 여러 procedure group을 한 번에 보고,
#    bed_type을 "합집합"으로 묶어 effective_beds를 계산
def get_effective_beds_for_groups(
    hpid: str,
    realtime: HospitalRealtime,
    group_ids: Iterable[str],
) -> Tuple[int, int, List[str]]:
    """
    여러 procedure group에 대해, 겹치는 bed_type을 합집합으로 묶어서 한 번만 카운트.

    예)
      required_groups = ["ACS_MI", "BRONCHOSCOPY", "GI_ENDOSCOPY"]

      - 각 그룹의 bed_types:
          ACS_MI        -> ["er", "icu_general"]
          BRONCHOSCOPY  -> ["er", "icu_general"]
          GI_ENDOSCOPY  -> ["er", "ward"]

      - 합집합 bed_types: {"er", "icu_general", "ward"}

      ⇒ 이 합집합에 대해 병상 수를 계산 (er/icu_general이 중복으로 더해지지 않음)

    return:
      (api_beds_total, effective_beds_total, used_bed_types)
    """
    if not realtime:
        return 0, 0, []

    # 1) group들에서 bed_type 합집합 생성
    bed_type_set: set[str] = set()
    for gid in group_ids:
        cfg = PROCEDURE_GROUPS.get(gid)
        if not cfg:
            continue
        bed_type_set.update(cfg["bed_types"])

    if not bed_type_set:
        return 0, 0, []

    # 2) 각 bed_type별 가용 병상 수 합산 (타입별로 한 번씩만)
    api_beds_total = 0
    for bt in bed_type_set:
        func = BED_TYPE_FUNCS.get(bt)
        if not func:
            continue
        api_beds_total += max(func(realtime), 0)

    if api_beds_total <= 0:
        return 0, 0, sorted(bed_type_set)

    # 3) pending_assignments를 bed_type 합집합 기준으로 모두 반영
    pending_total = 0
    for bt in bed_type_set:
        pending_total += pending_assignments[hpid][bt]

    effective_total = max(api_beds_total - pending_total, 0)
    return api_beds_total, effective_total, sorted(bed_type_set)


def procedure_status_for_hospital(
    summary: HospitalSummary,
    required_groups: List[str],
) -> Dict[str, Dict[str, int]]:
    """
    summary + 필요한 procedure 그룹 리스트를 넣으면,
    각 그룹에 대해 {"api_beds": X, "effective_beds": Y}를 계산해서 반환.

    - 수술/시술 가능 여부 자체(가능/불가능/차단)는
      compute_procedure_availability() 결과(= summary.procedure_availability)를 신뢰.
    - status != "가능" 이면 병상 수는 0으로 본다.

       complaint 단위로 "총 몇 병상?"이 궁금하다면,
       이 함수 결과를 단순 합산하지 말고,
       get_effective_beds_for_groups()를 사용해서
       bed_type 합집합 기준으로 다시 계산해야 한다.
    """
    result: Dict[str, Dict[str, int]] = {}

    # 이미 summary에 채워져 있으면 그걸 쓰고, 없으면 다시 계산
    if summary.procedure_availability:
        proc_avail = summary.procedure_availability
    else:
        proc_avail = compute_procedure_availability(summary)

    for group_id in required_groups:
        cfg = PROCEDURE_GROUPS.get(group_id)
        if not cfg:
            continue

        avail = proc_avail.get(group_id)
        # 아예 정보가 없거나, status가 "가능"이 아니면 병상은 0 처리
        if not avail or avail.status != "가능":
            result[group_id] = {"api_beds": 0, "effective_beds": 0}
            continue

        # 병상 정보 자체가 없으면 역시 0
        if not summary.realtime:
            result[group_id] = {"api_beds": 0, "effective_beds": 0}
            continue

        api_beds, eff_beds = get_effective_beds(
            summary.id,
            summary.realtime,
            cfg["bed_types"],
        )

        result[group_id] = {
            "api_beds": api_beds,
            "effective_beds": eff_beds,
        }

    return result
