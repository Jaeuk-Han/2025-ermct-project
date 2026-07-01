# RAG KTAS Parser Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate RAG KTAS responses deterministically and ensure the final KTAS is never less urgent than the rule-based baseline.

**Architecture:** `app/ktas_rag.py` owns staged JSON parsing and Pydantic candidate validation. `app/ktas_engine.py` always computes the rule baseline and applies confidence/evidence gates plus `min(rule, rag)`, while `app/ktas_normalizer.py` carries backward-compatible optional metadata.

**Tech Stack:** Python 3.11, Pydantic 2, unittest, Poetry

---

### Task 1: Staged parser and candidate schema

**Files:**
- Modify: `app/ktas_rag.py`
- Create: `tests/test_ktas_rag.py`

- [ ] Add parser tests for direct JSON, fenced JSON, surrounding prose, `ktas_level="3"`, KTAS 0/6, confidence outside 0–1, list evidence, aliases, and malformed text.
- [ ] Run `poetry run python -m unittest tests.test_ktas_rag -v`; expect failures for unsupported parsing and validation.
- [ ] Add `RagKtasCandidate` with `Field(ge=1, le=5)`, confidence bounds, list evidence, default-factory warnings, and alias normalization.
- [ ] Implement direct load, fence removal, and `JSONDecoder.raw_decode` extraction without repair calls or clamping.
- [ ] Strengthen the prompt to require JSON only, no fences/external explanation, bounded fields, and provided evidence only.
- [ ] Run the focused module; expect all parser tests to pass.

### Task 2: Rule baseline and safety merge

**Files:**
- Modify: `app/ktas_normalizer.py`
- Modify: `app/ktas_engine.py`
- Modify: `tests/test_ktas_engine.py`

- [ ] Add engine tests for valid RAG metadata, empty evidence, low confidence, malformed/invalid RAG fallback, rule=2/RAG=4, and rule=4/RAG=2.
- [ ] Run `poetry run python -m unittest tests.test_ktas_engine -v`; expect failures for missing baseline metadata and merge behavior.
- [ ] Extend `NormalizedKTASResult` with optional rule/RAG levels, RAG confidence, and `safety_merge_applied`.
- [ ] Compute rule baseline before RAG classification, preserve rule-based method on parse/schema exceptions, and otherwise select rule for low confidence/empty evidence or `min(rule, rag)`.
- [ ] Keep `ktas_method="rag_based"` for structurally valid RAG and set stable fallback reasons.
- [ ] Run focused engine and stage1 response tests; expect all to pass.

### Task 3: Full verification

**Files:**
- Verify only

- [ ] Run `poetry run python -m compileall app`; expect exit 0.
- [ ] Run `poetry run python -m unittest discover -s tests -v`; expect all tests to pass without real LLM calls.
- [ ] Run `git diff --check` and inspect `git diff --name-only`; expect only RAG files, tests, and approved docs.
