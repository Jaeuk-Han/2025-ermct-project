# Nearest Top3 Order Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Return `/api/ktas/route/seoul/nearest` hospitals in deterministic TMAP ranking order without changing capability scoring.

**Architecture:** Preserve HPID and tie-break metadata through the distance layer, sort successful results centrally in `get_top3`, and build endpoint responses by iterating those sorted results. Keep all existing response fields and frontend behavior.

**Tech Stack:** Python 3.11, FastAPI, unittest, Poetry

---

### Task 1: Distance result identity and deterministic sort

**Files:**
- Modify: `app/distance_logic.py`
- Create: `tests/test_nearest_ranking.py`

- [ ] Add tests proving distance, duration, coverage, and priority tie-break order plus exclusion of failed TMAP results.
- [ ] Run `poetry run python -m unittest tests.test_nearest_ranking -v`; expect failures because IDs/metadata are not preserved and only distance is sorted.
- [ ] Preserve `id`, `coverage_score`, and `priority_score` in successful distance results.
- [ ] Sort using `(distance, missing_duration, duration, -coverage_score, -priority_score)` and return at most three.
- [ ] Re-run the focused module; expect distance-layer tests to pass.

### Task 2: Endpoint response order and HPID mapping

**Files:**
- Modify: `app/main.py`
- Modify: `tests/test_nearest_ranking.py`

- [ ] Add async endpoint tests for the Severance regression, original-priority-order regression, duplicate names, and partial TMAP success.
- [ ] Run the focused module; expect endpoint ordering and HPID assertions to fail.
- [ ] Include HPID and tie-break metadata in the distance payload, index request hospitals by HPID, and iterate `top3_results` when constructing the response.
- [ ] Re-run focused tests; expect all nearest ranking tests to pass.

### Task 3: Full verification

**Files:**
- Verify only

- [ ] Run `poetry run python -m compileall app`; expect exit 0.
- [ ] Run `poetry run python -m unittest discover -s tests -v`; expect all tests to pass.
- [ ] Run `git diff --check` and inspect changed filenames; expect only `app/main.py`, `app/distance_logic.py`, nearest tests, and approved docs.
