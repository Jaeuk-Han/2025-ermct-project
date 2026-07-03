from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, model_validator

load_dotenv()

_cached_client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    global _cached_client
    if _cached_client is None:
        import os

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file.")
        _cached_client = OpenAI(api_key=api_key)
    return _cached_client

GPT_MODEL = "gpt-5.5"
# 저가 모델: 클리닝/SBAR추출/중분류선택 등 "쉬운" 작업용. RAG 추론(GPT_MODEL)만 최고가 유지.
# gpt-5.5-mini가 이 키에서 안 되면 .env에 ERMCT_LIGHT_MODEL=<정확한 모델명> 지정.
LIGHT_MODEL = os.getenv("ERMCT_LIGHT_MODEL", "gpt-5.5-mini")
EMBEDDING_MODEL = "text-embedding-3-large"


# =====================================================
# KTAS 대분류(신체계통) taxonomy — RAG 가지(branch) 필터용
# =====================================================
# LLM이 SBAR에서 뱉은 ktas_categories 값을 아래 정식 CSV category 문자열로 정규화한다.
# '첫인상 평가'는 LLM이 고르는 대상이 아니라, 필터 시 항상 포함되는 중증 안전 가지다.

KTAS_CATEGORIES = [
    "소화기계", "임신/여성생식계", "피부", "비뇨기계/남성생식계", "근골격계", "일반",
    "신경계", "심혈관계", "입,목/얼굴", "몸통외상", "호흡기계", "환경손상",
    "코", "물질오용", "눈", "정신건강", "귀",
]
FIRST_IMPRESSION_CATEGORY = "첫인상 평가(명백한 중증)"


def _normalize_category_key(value: str) -> str:
    # 구두점/공백 차이를 무시하고 매칭 (예: "입/목/얼굴" ~ "입,목/얼굴")
    return re.sub(r"[\s,/()·]", "", value or "")


_CATEGORY_LOOKUP = {_normalize_category_key(c): c for c in KTAS_CATEGORIES}


def canonicalize_categories(raw: Any) -> List[str]:
    """LLM이 뱉은 대분류 값을 정식 CSV category 문자열로 정규화. 목록 밖 값은 버린다."""
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [raw]
    result: List[str] = []
    for item in raw:
        canonical = _CATEGORY_LOOKUP.get(_normalize_category_key(str(item)))
        if canonical and canonical not in result:
            result.append(canonical)
    return result


# chief_complaint(enum) → 한국어 임상어 (RAG 쿼리를 코퍼스 어휘에 맞추기 위함)
_CC_KO = {
    "chest_pain": "흉통", "dyspnea": "호흡곤란", "neuro": "신경학적 증상",
    "abdominal": "복통", "bleeding": "출혈", "altered": "의식 변화",
    "trauma": "외상", "obgyn": "산과 응급", "pediatric": "소아 응급",
    "psychiatric": "정신과적 증상",
}
_SEV_KO = {"severe": "중증", "moderate": "중등도", "mild": "경증"}


def build_rag_query(clean_text: str, sbar: dict) -> str:
    """
    RAG 검색용 쿼리를 코퍼스 어휘(한국어 증상 + 중증도)에 맞춰 구성한다.
    SBAR JSON을 통째로 넣지 않는다 — 영어 필드명/null/false가 임베딩 노이즈가 되기 때문.
    """
    S = sbar.get("S") or {}
    parts: List[str] = []

    # 증상어를 맨 앞에(검색 앵커) — symptom_text 우선, 없으면 enum→한국어.
    # cc=None(enum 밖)이어도 symptom_text로 앵커를 확보해 보일러플레이트 오염을 줄인다.
    sev = _SEV_KO.get(str(S.get("severity") or "").strip().lower())
    symptom = (S.get("symptom_text") or "").strip()
    if not symptom:
        symptom = _CC_KO.get(str(S.get("chief_complaint") or "").strip().lower(), "")
    if symptom:
        parts.append(f"{sev} {symptom}" if sev else symptom)  # 예: "중등도 호흡곤란"

    if clean_text and clean_text.strip():
        parts.append(clean_text.strip())

    return "\n".join(parts) if parts else (clean_text or "")


def classify_subcategory(
    symptom_text: Optional[str],
    categories: List[str],
    cat2sub: Dict[str, List[str]],
    max_pick: int = 2,
) -> List[str]:
    """
    2차 LLM 호출: 이미 정해진 대분류(들)의 중분류 목록만 보여주고, 증상어에 맞는 것을 고른다.
    실패/애매하면 빈 리스트 → 호출부에서 대분류-only 필터로 폴백.
    """
    if not symptom_text or not categories:
        return []
    options = sorted({s for c in categories for s in cat2sub.get(c, [])})
    if not options:
        return []

    prompt = (
        f"환자 증상: {symptom_text}\n"
        f"아래 중분류 목록에서 이 증상에 가장 맞는 것을 최대 {max_pick}개 고르시오.\n"
        f"정말 애매하면 빈 배열 []. 목록의 문자열을 토씨 그대로 사용. JSON 배열만 반환.\n"
        f"목록: {options}"
    )
    try:
        resp = get_openai_client().chat.completions.create(
            model=LIGHT_MODEL,
            messages=[
                {"role": "system", "content": "너는 KTAS 중분류 선택기다. JSON 문자열 배열만 반환한다."},
                {"role": "user", "content": prompt},
            ],
        )
        raw = resp.choices[0].message.content or "[]"
        m = re.search(r"\[.*\]", raw, re.S)
        picked = json.loads(m.group(0)) if m else []
    except Exception:
        return []  # 2차 호출 실패 시 조용히 대분류-only로 폴백

    opt_lookup = {_normalize_category_key(o): o for o in options}
    result: List[str] = []
    for p in picked:
        canonical = opt_lookup.get(_normalize_category_key(str(p)))
        if canonical and canonical not in result:
            result.append(canonical)
    return result[:max_pick]


class RagResponseParseError(ValueError):
    pass


class RagKtasCandidate(BaseModel):
    ktas: int = Field(..., ge=1, le=5)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = ""
    evidence: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        normalized = dict(value)
        if normalized.get("ktas") is None:
            normalized["ktas"] = normalized.get("ktas_level")
        if not normalized.get("reason"):
            normalized["reason"] = normalized.get("primary_reason") or ""
        warnings = normalized.get("warnings") or []
        if not normalized["reason"] and "reason_missing" not in warnings:
            warnings = [*warnings, "reason_missing"]
        normalized["warnings"] = warnings
        return normalized

@dataclass
class KtasGuidelineDoc:
    id: str
    title: str
    ktas_level: Optional[int]
    category: Optional[str]
    sub_category: Optional[str]
    text: str
    source: str
    age_group: Optional[str] = None
    first_impression: bool = False
    embedding: Optional[list[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "ktas_level": self.ktas_level,
            "category": self.category,
            "sub_category": self.sub_category,
            "text": self.text,
            "source": self.source,
            "age_group": self.age_group,
            "first_impression": self.first_impression,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KtasGuidelineDoc":
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            ktas_level=data.get("ktas_level"),
            category=data.get("category"),
            sub_category=data.get("sub_category"),
            text=data.get("text", ""),
            source=data.get("source", ""),
            age_group=data.get("age_group"),
            first_impression=data.get("first_impression", False),
            embedding=data.get("embedding"),
        )


def build_cat2sub(docs: List["KtasGuidelineDoc"]) -> Dict[str, List[str]]:
    """인덱스에서 대분류→중분류 목록 매핑을 생성 (2차 LLM 호출에 넘길 후보)."""
    from collections import defaultdict

    m: Dict[str, set] = defaultdict(set)
    for d in docs:
        cat, sub = getattr(d, "category", None), getattr(d, "sub_category", None)
        if cat and sub and cat not in KTAS_CATEGORIES_EXCLUDE:
            m[cat].add(sub)
    return {c: sorted(v) for c, v in m.items()}


# 대분류 자리에 잘못 들어온 헤더 잔여값(빌드 스크립트가 헤더 1줄만 스킵해서 생김)
KTAS_CATEGORIES_EXCLUDE = {"3단계"}


class KtasVectorStore:
    def __init__(self, docs: Optional[List[KtasGuidelineDoc]] = None) -> None:
        self.docs = docs or []
        self.embedding_model = EMBEDDING_MODEL
        self.cat2sub = build_cat2sub(self.docs)

    @classmethod
    def load(cls, path: Path) -> "KtasVectorStore":
        data = json.loads(path.read_text(encoding="utf-8"))
        docs = [KtasGuidelineDoc.from_dict(item) for item in data["documents"]]
        return cls(docs=docs)

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "documents": [doc.to_dict() for doc in self.docs],
                    "created_by": "Yu Won Lee",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def encode_text(self, text: str) -> list[float]:
        if not text.strip():
            return []
        response = get_openai_client().embeddings.create(model=self.embedding_model, input=text)
        return response.data[0].embedding

    @staticmethod
    def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
        a_list = list(a)
        b_list = list(b)
        if not a_list or not b_list or len(a_list) != len(b_list):
            return 0.0
        dot = sum(x * y for x, y in zip(a_list, b_list))
        norm_a = math.sqrt(sum(x * x for x in a_list))
        norm_b = math.sqrt(sum(y * y for y in b_list))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def query(
        self,
        text: str,
        top_k: int = 5,
        categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        include_first_impression: bool = True,
    ) -> List[Dict[str, Any]]:
        query_embedding = self.encode_text(text)
        if not query_embedding:
            return []

        # 계층 필터: 대분류(+ 지정 시 중분류)로 후보를 좁힘 + 첫인상평가는 항상 포함.
        # categories가 비면 전체 검색. sub_categories가 비면 대분류까지만 좁힘.
        category_set = set(categories) if categories else None
        sub_set = set(sub_categories) if sub_categories else None

        hits: list[Dict[str, Any]] = []
        for doc in self.docs:
            if not doc.embedding:
                continue
            if category_set is not None:
                in_branch = doc.category in category_set
                if in_branch and sub_set is not None:
                    in_branch = doc.sub_category in sub_set
                is_critical = include_first_impression and doc.first_impression
                if not (in_branch or is_critical):
                    continue
            score = self.cosine_similarity(query_embedding, doc.embedding)
            hits.append({"doc": doc, "score": score})

        hits.sort(key=lambda item: item["score"], reverse=True)
        return [
            {
                "id": item["doc"].id,
                "title": item["doc"].title,
                "ktas_level": item["doc"].ktas_level,
                "category": item["doc"].category,
                "sub_category": item["doc"].sub_category,
                "text": item["doc"].text,
                "source": item["doc"].source,
                "first_impression": item["doc"].first_impression,
                "age_group": item["doc"].age_group,
                "score": item["score"],
            }
            for item in hits[:top_k]
        ]


def build_rag_prompt(clean_text: str, sbar: dict, retrieved_docs: List[Dict[str, Any]]) -> str:
    guidance = [
        "당신은 한국 성인 응급환자의 KTAS 분류 전문가입니다.",
        "이 분류는 성인 환자만 대상으로 합니다. 소아/영유아 기준은 무시하세요.",
        "첫인상 평가는 5초 이내에 파악 가능한 중증 신호에 한정합니다.",
        "KTAS 1은 무의식, 중증 호흡곤란, 중증 탈수 또는 즉각적 소생/순환 지원이 필요한 경우(명백한 쇼크, 명백한 의식소실)로 제한합니다.",
        "KTAS 1~5는 중증도 단계로, 문맥과 기준에 따라 3가지 후보를 추천하십시오.",
        "반드시 KTAS 1~5 숫자 형태로 반환합니다.",
        "Return JSON only.",
        "Do not include markdown fences.",
        "Do not include explanations outside JSON.",
        "ktas 또는 ktas_level은 1부터 5 사이의 정수여야 합니다.",
        "confidence는 0.0부터 1.0 사이의 실수여야 합니다.",
        "정보가 부족하면 값을 만들어내지 말고 null 또는 unknown을 사용하십시오.",
        "제공된 검색 evidence만 사용하십시오.",
        "evidence가 부족하면 confidence를 0.5 이하로 설정하고 warning을 추가하십시오.",
        # ↓ 숫자 티어 매핑: 검색 문서에 적힌 수치 기준을 환자 실제 값에 정확히 대입한다.
        "검색된 문서에 수치 기준(예: NRS 4-7, GCS 9-13, SpO2 85%, 수축기혈압 90 미만, 급성 통증(8-10))이 있으면, 환자의 실제 수치를 그 범위에 대입해 일치하는 문서의 KTAS를 고르십시오.",
        "경계값은 문서에 표기된 범위 그대로 포함해 판단하십시오. 예: NRS가 4이면 '(<4)'가 아니라 '(4-7)' 구간에 속합니다.",
        "환자 수치를 근거 없이 더 위급하거나 덜 위급한 구간으로 옮기지 말고, 수치가 실제로 속하는 구간의 문서를 따르십시오.",
        # ↓ 조건 수식어 가드: 환자에 해당하지 않는 수식어가 붙은 문서의 KTAS를 그대로 적용하지 않는다.
        "문서에 붙은 조건 수식어(예: 만성/chronic, 급성/acute, 면역저하, 열 동반 등)가 환자 상태와 다르면 그 문서의 KTAS를 적용하지 마십시오.",
        "특히 환자가 급성 증상인데 '정상 활력징후' 문서가 '만성' 조건뿐이라면, 그 만성 문서의 낮은 KTAS(예: 5)를 급성 환자에 적용하지 말고 급성 기본값(중등도, 통상 KTAS 3)으로 판단하십시오.",
        "설명은 한국어로 작성하십시오."
    ]

    evidence_text = "\n\n".join(
        f"[{idx + 1}] id={doc['id']} ktas={doc.get('ktas_level')} title={doc['title']} score={doc['score']:.4f}\n{doc['text']}"
        for idx, doc in enumerate(retrieved_docs)
    )

    prompt = f"""
{chr(10).join(guidance)}

검색된 KTAS 가이드라인 문서:
{evidence_text}

환자 입력 원문:
{clean_text}

SBAR 구조화:
{sbar}

요청:
- 위 내용을 참고해 성인 환자의 KTAS 후보 3개를 추천하십시오.
- 각 후보는 ktas, reason, confidence(0.0~1.0) 필드를 가져야 합니다.
- confidence는 문맥과 검색된 가이드라인의 적합성을 반영하십시오.
- evidence 필드에는 참고한 문서 id를 1개 이상 포함하십시오.
- return only JSON array.
""".strip()
    return prompt


def parse_rag_response(text: str) -> List[Dict[str, Any]]:
    def as_candidates(value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, dict):
            return [value]
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return value
        raise ValueError("RAG 출력이 dict 또는 dict 리스트 형식이 아닙니다.")

    cleaned = text.strip()
    try:
        return as_candidates(json.loads(cleaned))
    except (json.JSONDecodeError, ValueError):
        pass

    lines = cleaned.splitlines()
    if lines and lines[0].strip().startswith("```"):
        fenced_lines = lines[1:]
        if fenced_lines and fenced_lines[-1].strip() == "```":
            fenced_lines = fenced_lines[:-1]
        fenced = "\n".join(fenced_lines).strip()
        try:
            return as_candidates(json.loads(fenced))
        except (json.JSONDecodeError, ValueError):
            pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(cleaned):
        if char not in "[{":
            continue
        try:
            parsed, _ = decoder.raw_decode(cleaned, index)
            return as_candidates(parsed)
        except (json.JSONDecodeError, ValueError):
            continue

    raise RagResponseParseError(
        "RAG 출력 JSON 파싱에 실패했습니다. 출력 텍스트를 확인하세요."
    )


def normalize_candidate(candidate: dict, top_similarity: float) -> dict:
    validated = RagKtasCandidate.model_validate(candidate)
    return validated.model_dump()


def classify_ktas_rag(
    clean_text: str,
    sbar: dict,
    vector_store: KtasVectorStore,
    top_k: int = 5,
    candidate_count: int = 3,
) -> List[Dict[str, Any]]:
    S = sbar.get("S") or {}
    categories = canonicalize_categories(S.get("ktas_categories"))
    # 2차 LLM: 대분류가 정해졌으면 그 안 중분류를 증상어로 좁힘 (실패/애매하면 [])
    subcategories = (
        classify_subcategory(S.get("symptom_text"), categories, vector_store.cat2sub)
        if categories
        else []
    )
    query_text = build_rag_query(clean_text, sbar)

    # 계층 폴백 체인: 대분류∩중분류 → 대분류만 → 전체.
    # 중분류로 좁히면 leaf가 적으니(≤~20) top_k를 키워 모든 중증도 티어를 재추론에 통째로 넘김.
    leaf_k = max(top_k, 20) if categories else top_k
    retrieved = vector_store.query(
        query_text,
        top_k=leaf_k,
        categories=categories or None,
        sub_categories=subcategories or None,
    )
    if not retrieved and subcategories:  # 중분류 필터가 너무 빡세면 중분류만 풀기
        retrieved = vector_store.query(query_text, top_k=leaf_k, categories=categories or None)
    if not retrieved and categories:  # 대분류까지 풀기
        retrieved = vector_store.query(query_text, top_k=top_k, categories=None)

    if not retrieved:
        raise RuntimeError("RAG vector store에서 검색된 문서가 없습니다.")

    prompt = build_rag_prompt(clean_text, sbar, retrieved)
    response = get_openai_client().chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "KTAS RAG 추천 엔진입니다. 반드시 JSON 배열만 반환하세요."},
            {"role": "user", "content": prompt},
        ]
    )

    raw_output = response.choices[0].message.content
    candidates = parse_rag_response(raw_output)

    top_similarity = retrieved[0]["score"] if retrieved else 0.0
    normalized = [normalize_candidate(c, top_similarity) for c in candidates][:candidate_count]

    if len(normalized) < candidate_count:
        seen = {(item["ktas"], item["reason"]) for item in normalized}
        for doc in retrieved:
            if len(normalized) >= candidate_count:
                break
            if doc["ktas_level"] is None:
                continue
            fallback = {
                "ktas": int(doc["ktas_level"]),
                "reason": (
                    f"검색된 지침 문서 {doc['id']}에서 유사 KTAS {doc['ktas_level']}로 추정"
                ),
                "confidence": max(0.15, min(0.65, float(doc["score"]))),
                "evidence": [doc["id"]],
            }
            if (fallback["ktas"], fallback["reason"]) not in seen:
                normalized.append(fallback)
                seen.add((fallback["ktas"], fallback["reason"]))

    normalized.sort(key=lambda item: item["confidence"], reverse=True)
    return normalized[:candidate_count]
