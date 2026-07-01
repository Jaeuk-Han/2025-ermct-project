# RAG Nonurgent Merge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow validated RAG KTAS 4–5 results when the rule baseline is 3 while preserving rule 1–2 safety priority.

**Architecture:** Change only the valid-RAG merge branch in `app/ktas_engine.py`. Preserve confidence/evidence gates and parse/validation fallback contracts, and verify policy through focused engine tests.

**Tech Stack:** Python 3.11, unittest, Poetry

---

### Task 1: Policy regression tests

**Files:**
- Modify: `tests/test_ktas_engine.py`

- [ ] Replace the obsolete rule=2/RAG=4 expectation and add rule=3/RAG=4, rule=3/RAG=5, rule=3/RAG=2, rule=2/RAG=3, and rule=1/RAG=4 assertions.
- [ ] Retain and verify low-confidence, empty-evidence, parse-failure, and validation-failure tests.
- [ ] Run `poetry run python -m unittest tests.test_ktas_engine -v`; expect RAG 4–5 allowance tests to fail under unconditional `min`.

### Task 2: Minimal merge branch change

**Files:**
- Modify: `app/ktas_engine.py`

- [ ] Keep confidence/evidence branches unchanged.
- [ ] For valid RAG 1–3, keep `min(rule_level, rag_level)`.
- [ ] For valid RAG 4–5 with rule 1–2, select rule and set `rule_based_safety_priority`.
- [ ] For valid RAG 4–5 with rule 3, select RAG with no fallback reason.
- [ ] Keep `safety_merge_applied` defined as final level differing from the original RAG level.
- [ ] Run focused engine tests; expect all policy tests to pass.

### Task 3: Full verification

**Files:**
- Verify only

- [ ] Run `poetry run python -m compileall app`; expect exit 0.
- [ ] Run `poetry run python -m unittest discover -s tests -v`; expect all tests to pass.
- [ ] Run `git diff --check` and verify only `app/ktas_engine.py`, `tests/test_ktas_engine.py`, and approved docs changed.
