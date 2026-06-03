from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, HTTPException

from app.complaint_mapping import required_procedure_groups_for_complaint
from app.procedure_groups import PROCEDURE_GROUPS
from app.schemas import BedReleaseRequest, BedReservationRequest
from app.state_assignments import pending_assignments
from app.triage_utils import choose_primary_bed_type


router = APIRouter()


@router.post("/api/triage/reservations")
def create_bed_reservation(req: BedReservationRequest):
    """
    선택된 병원(hpid)에 대해
    - complaint_id -> procedure group -> bed_types 체인으로
    - 우리 쪽 in-memory pending_assignments에 '예약'을 반영하는 API.

    지금은 '1 환자 = 대표 bed_type 1개(보통 ER)'만 예약으로 반영한다.
    이후 /api/triage/candidates, /api/hospitals/procedure-beds/by-region 등에서
    get_effective_beds()를 통해 자동으로 감산된 병상 수가 반영됨.
    """
    groups = required_procedure_groups_for_complaint(req.complaint_id)
    if not groups:
        raise HTTPException(status_code=400, detail="지원하지 않는 complaint_id 입니다.")

    bed_types: set[str] = set()
    for gid in groups:
        cfg = PROCEDURE_GROUPS.get(gid)
        if not cfg:
            continue
        for bt in cfg["bed_types"]:
            bed_types.add(bt)

    if not bed_types:
        raise HTTPException(
            status_code=400,
            detail="해당 complaint에 매핑된 bed_types가 없습니다.",
        )

    primary_bed_type = choose_primary_bed_type(bed_types)
    if not primary_bed_type:
        raise HTTPException(
            status_code=400,
            detail="예약에 사용할 bed_type을 결정할 수 없습니다.",
        )

    hospital_assign = pending_assignments[req.hpid]
    hospital_assign[primary_bed_type] += req.num_patients

    return {
        "hpid": req.hpid,
        "complaint_id": req.complaint_id,
        "ktas": req.ktas,
        "num_patients": req.num_patients,
        "reserved_bed_types": [primary_bed_type],
        "pending_assignments": dict(hospital_assign),
    }


@router.post("/api/triage/reservations/release")
def release_bed_reservation(req: BedReleaseRequest):
    """
    in-memory pending_assignments에서 예약을 되돌리는 API.
    - 지금은 create와 마찬가지로 '대표 bed_type 1개(보통 ER)'에 대해서만 해제한다.
    - 실제 운영이면 '환자 도착 취소/오류' 같은 상황을 표현할 때 사용.
    """
    groups = required_procedure_groups_for_complaint(req.complaint_id)
    if not groups:
        raise HTTPException(status_code=400, detail="지원하지 않는 complaint_id 입니다.")

    bed_types: set[str] = set()
    for gid in groups:
        cfg = PROCEDURE_GROUPS.get(gid)
        if not cfg:
            continue
        for bt in cfg["bed_types"]:
            bed_types.add(bt)

    if not bed_types:
        raise HTTPException(
            status_code=400,
            detail="해당 complaint에 매핑된 bed_types가 없습니다.",
        )

    primary_bed_type = choose_primary_bed_type(bed_types)
    if not primary_bed_type:
        raise HTTPException(
            status_code=400,
            detail="해제에 사용할 bed_type을 결정할 수 없습니다.",
        )

    hospital_assign = pending_assignments[req.hpid]

    current = hospital_assign[primary_bed_type]
    hospital_assign[primary_bed_type] = max(current - req.num_patients, 0)

    return {
        "hpid": req.hpid,
        "complaint_id": req.complaint_id,
        "num_patients": req.num_patients,
        "released_bed_types": [primary_bed_type],
        "pending_assignments": dict(hospital_assign),
    }


@router.get("/debug/triage/pending-assignments")
def debug_pending_assignments():
    """
    현재 프로세스 메모리에 쌓여 있는 pending_assignments 딕셔너리를 그대로 보여준다.
    (졸업작품 시연/디버깅용)
    """
    out: Dict[str, Dict[str, int]] = {}
    for hpid, bed_map in pending_assignments.items():
        out[hpid] = dict(bed_map)
    return out
