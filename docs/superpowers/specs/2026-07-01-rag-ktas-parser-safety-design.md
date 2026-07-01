# RAG KTAS Parser Safety Design

## Scope

Stabilize RAG KTAS parsing and add conservative rule-based safety merging. Route fallback, administrative-code mapping, deployment configuration, public API budgets, and frontend UI are out of scope.

## Parsing and validation

`app/ktas_rag.py` will parse in three deterministic stages: direct `json.loads`, fenced-content parsing, then `JSONDecoder.raw_decode` scanning for the first valid object or array. It will not make repair LLM calls. A Pydantic `RagKtasCandidate` will accept `ktas` or `ktas_level` and `reason` or `primary_reason`, coercing numeric strings while rejecting KTAS outside 1–5, confidence outside 0–1, and non-list evidence. Empty evidence remains structurally valid so the engine can apply an explicit safety fallback.

## Engine safety policy

For every RAG request, the engine computes the rule-based baseline first. Parsing or schema failure preserves current fallback behavior: `ktas_method="rule_based"`, `fallback_from="rag_based"`. A valid RAG result keeps `ktas_method="rag_based"`; confidence below 0.6 or empty evidence selects the rule baseline, otherwise the final level is `min(rule_based, rag_based)`. This prevents RAG from making the patient less urgent.

## Compatibility metadata

Existing fields remain unchanged. `NormalizedKTASResult` and the engine response gain optional `rule_based_ktas`, `rag_based_ktas`, `rag_confidence`, and `safety_merge_applied`. `fallback_reason` uses stable values such as `rag_confidence_low`, `rag_evidence_empty`, `rag_less_urgent_than_rule`, `rag_parse_failed`, and `rag_validation_failed`.

## Testing

Unit tests mock all LLM/RAG boundaries and cover direct, fenced, and mixed-text JSON; numeric strings; invalid KTAS/confidence; empty evidence; malformed responses; and both directions of rule/RAG urgency conflict. Validation uses Poetry compileall, full unittest discovery, and `git diff --check`.
