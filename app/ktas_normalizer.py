from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


KTASMethod = Literal["rule_based", "rag_based"]


class NormalizedKTASResult(BaseModel):
    ktas_level: int
    chief_complaint: str
    reason: str
    method: KTASMethod
    confidence: float | None = None
    evidence: list[str] = Field(default_factory=list)
    ktas_options: list[dict[str, Any]] = Field(default_factory=list)
    sbar: dict[str, Any] = Field(default_factory=dict)
    hospital_followup: str | None = None
    fallback_from: str | None = None
    fallback_reason: str | None = None
    rule_based_ktas: int | None = None
    rag_based_ktas: int | None = None
    rag_confidence: float | None = None
    safety_merge_applied: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


def normalize_rule_based_result(
    *,
    ktas_result: dict[str, Any],
    sbar: dict[str, Any],
    raw_hospital: str | None = None,
    final_hospital: str | None = None,
    fallback_from: str | None = None,
    fallback_reason: str | None = None,
) -> NormalizedKTASResult:
    llm_hospital = (sbar.get("B") or {}).get("followup_hospital")
    chief_complaint = (sbar.get("S") or {}).get("chief_complaint") or "unknown"

    return NormalizedKTASResult(
        ktas_level=int(ktas_result.get("ktas", 0) or 0),
        chief_complaint=str(chief_complaint),
        reason=str(ktas_result.get("reason") or ""),
        method="rule_based",
        confidence=1.0,
        sbar=sbar,
        hospital_followup=final_hospital or raw_hospital or llm_hospital,
        fallback_from=fallback_from,
        fallback_reason=fallback_reason,
        raw=ktas_result,
    )


def normalize_rag_based_result(
    *,
    ktas_options: list[dict[str, Any]],
    sbar: dict[str, Any],
    raw_hospital: str | None = None,
    final_hospital: str | None = None,
) -> NormalizedKTASResult:
    if not ktas_options:
        raise ValueError("RAG KTAS candidates are empty.")

    top_candidate = ktas_options[0]
    llm_hospital = (sbar.get("B") or {}).get("followup_hospital")
    chief_complaint = (sbar.get("S") or {}).get("chief_complaint") or "unknown"
    evidence = top_candidate.get("evidence") or []
    if isinstance(evidence, str):
        evidence = [evidence]
    if not isinstance(evidence, list):
        evidence = [str(evidence)]

    confidence = top_candidate.get("confidence")
    if confidence is not None:
        confidence = float(confidence)

    return NormalizedKTASResult(
        ktas_level=int(top_candidate.get("ktas", 0) or 0),
        chief_complaint=str(chief_complaint),
        reason=str(top_candidate.get("reason") or ""),
        method="rag_based",
        confidence=confidence,
        evidence=[str(item) for item in evidence],
        ktas_options=ktas_options,
        sbar=sbar,
        hospital_followup=final_hospital or raw_hospital or llm_hospital,
        raw=top_candidate,
    )
