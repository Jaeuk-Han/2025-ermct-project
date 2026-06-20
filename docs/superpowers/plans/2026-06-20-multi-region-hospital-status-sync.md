# Multi-Region Hospital Status Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing hospital status worker to synchronize an ordered set of ERMCT regions sequentially while retaining legacy single-region operation.

**Architecture:** Keep region fetch, normalization, and Supabase upsert logic in `run_sync_once()`. Add small configuration parsers and a `run_sync_cycle()` orchestrator that executes explicit targets in order, isolates target failures, delays only between targets, and returns an aggregate cycle status. Compose remains unchanged because it already passes `.env.production` into the worker.

**Tech Stack:** Python 3.11, Poetry, `unittest`, Docker Compose environment configuration

---

### Task 1: Specify target and delay configuration behavior

**Files:**
- Modify: `tests/test_sync_hospital_status.py`
- Modify: `scripts/sync_hospital_status.py`

- [ ] **Step 1: Add failing parser and fallback tests**

Import `argparse`, `patch`, `parse_sync_targets`, `parse_target_delay_seconds`, and `resolve_sync_targets`. Add tests that assert:

```python
def test_parse_sync_targets_preserves_order_and_trims_values(self) -> None:
    self.assertEqual(
        parse_sync_targets(" 서울특별시:강남구,서울특별시:서초구 "),
        [("서울특별시", "강남구"), ("서울특별시", "서초구")],
    )

def test_parse_sync_targets_rejects_malformed_or_empty_pairs(self) -> None:
    for value in ("서울특별시", ":강남구", "서울특별시:", "서울특별시:강남구,"):
        with self.subTest(value=value), self.assertRaisesRegex(
            ValueError,
            "HOSPITAL_STATUS_SYNC_TARGETS",
        ):
            parse_sync_targets(value)

def test_resolve_sync_targets_uses_legacy_single_region_when_targets_empty(self) -> None:
    args = argparse.Namespace(sido=None, sigungu=None)
    env = {
        "HOSPITAL_STATUS_SYNC_TARGETS": "  ",
        "HOSPITAL_STATUS_SYNC_SIDO": "경기도",
        "HOSPITAL_STATUS_SYNC_SIGUNGU": "성남시",
    }
    self.assertEqual(resolve_sync_targets(args, env), [("경기도", "성남시")])

def test_target_delay_defaults_to_three_and_accepts_zero(self) -> None:
    self.assertEqual(parse_target_delay_seconds(None), 3)
    self.assertEqual(parse_target_delay_seconds(""), 3)
    self.assertEqual(parse_target_delay_seconds("0"), 0)
    self.assertEqual(parse_target_delay_seconds(" 7 "), 7)

def test_target_delay_rejects_negative_or_non_integer_values(self) -> None:
    for value in ("-1", "abc", "1.5"):
        with self.subTest(value=value), self.assertRaisesRegex(
            ValueError,
            "HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS",
        ):
            parse_target_delay_seconds(value)
```

- [ ] **Step 2: Run focused tests and verify RED**

```powershell
poetry run python -m unittest tests.test_sync_hospital_status -v
```

Expected: import errors because the new helpers do not exist.

- [ ] **Step 3: Implement minimal parsing and resolution helpers**

Add:

```python
SyncTarget = tuple[str, str]


def parse_sync_targets(value: str) -> list[SyncTarget]:
    targets: list[SyncTarget] = []
    for index, raw_target in enumerate(value.split(","), start=1):
        target = raw_target.strip()
        if not target or target.count(":") != 1:
            raise ValueError(
                "Invalid HOSPITAL_STATUS_SYNC_TARGETS entry "
                f"#{index}: expected sido:sigungu"
            )
        sido, sigungu = (part.strip() for part in target.split(":", 1))
        if not sido or not sigungu:
            raise ValueError(
                "Invalid HOSPITAL_STATUS_SYNC_TARGETS entry "
                f"#{index}: sido and sigungu must be non-empty"
            )
        targets.append((sido, sigungu))
    return targets


def resolve_sync_targets(
    args: argparse.Namespace,
    environ: Mapping[str, str] = os.environ,
) -> list[SyncTarget]:
    configured = environ.get("HOSPITAL_STATUS_SYNC_TARGETS", "").strip()
    if configured:
        return parse_sync_targets(configured)
    sido = args.sido or environ.get("HOSPITAL_STATUS_SYNC_SIDO")
    sigungu = args.sigungu or environ.get("HOSPITAL_STATUS_SYNC_SIGUNGU")
    if not sido or not sigungu:
        raise ValueError("Single-region sync requires sido and sigungu")
    return [(sido, sigungu)]


def parse_target_delay_seconds(value: str | None) -> int:
    raw = (value or "").strip() or "3"
    try:
        delay = int(raw)
    except ValueError as exc:
        raise ValueError(
            "HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS must be a non-negative integer"
        ) from exc
    if delay < 0:
        raise ValueError(
            "HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS must be a non-negative integer"
        )
    return delay
```

Import `Mapping` from `typing`.

- [ ] **Step 4: Update environment validation for multi-target mode**

Change `missing_required_env()` so legacy region variables are required only when `HOSPITAL_STATUS_SYNC_TARGETS` is empty. Keep ERMCT and Supabase validation unchanged.

- [ ] **Step 5: Run focused tests and verify GREEN**

```powershell
poetry run python -m unittest tests.test_sync_hospital_status -v
```

Expected: all focused tests pass.

### Task 2: Specify and implement sequential cycle orchestration

**Files:**
- Modify: `tests/test_sync_hospital_status.py`
- Modify: `scripts/sync_hospital_status.py`

- [ ] **Step 1: Add failing cycle tests**

Import `run_sync_cycle`. Add tests using injected sync and sleep callables:

```python
def test_run_sync_cycle_processes_targets_sequentially_and_delays_between(self) -> None:
    args = argparse.Namespace()
    calls = []
    sleeps = []

    def sync_fn(_args, *, sido, sigungu):
        calls.append((sido, sigungu))
        return 0

    result = run_sync_cycle(
        args,
        [("서울특별시", "강남구"), ("서울특별시", "서초구")],
        target_delay_seconds=3,
        sync_fn=sync_fn,
        sleep_fn=sleeps.append,
    )

    self.assertEqual(result, 0)
    self.assertEqual(calls, [("서울특별시", "강남구"), ("서울특별시", "서초구")])
    self.assertEqual(sleeps, [3])

def test_run_sync_cycle_continues_after_failure_and_reports_partial_failure(self) -> None:
    args = argparse.Namespace()
    calls = []

    def sync_fn(_args, *, sido, sigungu):
        calls.append((sido, sigungu))
        return 1 if sigungu == "강남구" else 0

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        result = run_sync_cycle(
            args,
            [("서울특별시", "강남구"), ("서울특별시", "서초구")],
            target_delay_seconds=0,
            sync_fn=sync_fn,
        )

    self.assertEqual(result, 1)
    self.assertEqual(calls, [("서울특별시", "강남구"), ("서울특별시", "서초구")])
    self.assertIn("total_targets=2", output.getvalue())
    self.assertIn("succeeded_targets=1", output.getvalue())
    self.assertIn("failed_targets=1", output.getvalue())
    self.assertIn("status=partial-failed", output.getvalue())
```

- [ ] **Step 2: Run focused tests and verify RED**

```powershell
poetry run python -m unittest tests.test_sync_hospital_status -v
```

Expected: failures because `run_sync_cycle()` is missing.

- [ ] **Step 3: Allow explicit regions in `run_sync_once()`**

Change the signature without altering fetch/upsert behavior:

```python
def run_sync_once(
    args: argparse.Namespace,
    *,
    sido: str | None = None,
    sigungu: str | None = None,
) -> int:
    sido = sido or args.sido or os.environ["HOSPITAL_STATUS_SYNC_SIDO"]
    sigungu = sigungu or args.sigungu or os.environ["HOSPITAL_STATUS_SYNC_SIGUNGU"]
```

- [ ] **Step 4: Implement `run_sync_cycle()`**

Add a function that logs target start/result, catches exceptions per target, calls `sleep_fn()` only when another target remains, and prints one summary. Status is `success` when none fail, `failed` when all fail, and `partial-failed` otherwise. Return `1` whenever `failed_targets > 0`, otherwise `0`.

Use dependency injection defaults:

```python
def run_sync_cycle(
    args: argparse.Namespace,
    targets: Sequence[SyncTarget],
    target_delay_seconds: int,
    sync_fn: Callable[..., int] = run_sync_once,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> int:
```

Import `Callable` from `typing`.

- [ ] **Step 5: Run focused tests and verify GREEN**

```powershell
poetry run python -m unittest tests.test_sync_hospital_status -v
```

Expected: all focused tests pass.

### Task 3: Wire cycle orchestration into one-shot and interval modes

**Files:**
- Modify: `tests/test_sync_hospital_status.py`
- Modify: `scripts/sync_hospital_status.py`

- [ ] **Step 1: Add failing configuration and main-flow tests**

Use `patch.dict(os.environ, ..., clear=True)`, `patch()` for `run_sync_cycle`, and redirected output to verify:

- malformed target configuration makes `main([])` return `2` before synchronization;
- one-shot mode invokes one full cycle and returns its status;
- interval mode invokes the full cycle repeatedly and does not terminate after a returned failed status (stop the test with a `sleep` side effect after observing the first interval sleep).

- [ ] **Step 2: Run focused tests and verify RED**

```powershell
poetry run python -m unittest tests.test_sync_hospital_status -v
```

Expected: flow assertions fail because `main()` still calls `run_sync_once()`.

- [ ] **Step 3: Wire configuration into `main()`**

After existing missing-variable reporting, resolve targets and delay in a `try/except ValueError`. Print `Invalid sync configuration: <message>` and return `2` on validation failure.

One-shot mode returns:

```python
return run_sync_cycle(args, targets, target_delay_seconds)
```

Long-running mode calls the same cycle function, logs `exit_code`, sleeps `args.interval_seconds`, and continues regardless of cycle status.

- [ ] **Step 4: Run focused tests and verify GREEN**

```powershell
poetry run python -m unittest tests.test_sync_hospital_status -v
```

Expected: all focused tests pass.

### Task 4: Document production configuration and update deployment tests

**Files:**
- Modify: `.env.production.example`
- Modify: `tests/test_production_sync_worker.py`
- Verify unchanged: `docker-compose.prod.yml`

- [ ] **Step 1: Add failing environment-template assertions**

Extend the expected names with:

```python
"HOSPITAL_STATUS_SYNC_TARGETS",
"HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS",
```

Also assert the template contains a commented Seoul example and that the active targets assignment is blank.

- [ ] **Step 2: Run deployment tests and verify RED**

```powershell
poetry run python -m unittest tests.test_production_sync_worker -v
```

Expected: failure because the two environment entries are absent.

- [ ] **Step 3: Update `.env.production.example`**

Add below the legacy region variables:

```dotenv
# Optional multi-region mode. Leave blank to use the single-region values above.
HOSPITAL_STATUS_SYNC_TARGETS=
# Seoul example (all districts): HOSPITAL_STATUS_SYNC_TARGETS=서울특별시:강남구,서울특별시:서초구,서울특별시:송파구,서울특별시:강동구,서울특별시:광진구,서울특별시:성동구,서울특별시:용산구,서울특별시:중구,서울특별시:종로구,서울특별시:마포구,서울특별시:서대문구,서울특별시:은평구,서울특별시:동대문구,서울특별시:중랑구,서울특별시:성북구,서울특별시:강북구,서울특별시:도봉구,서울특별시:노원구,서울특별시:양천구,서울특별시:강서구,서울특별시:구로구,서울특별시:금천구,서울특별시:영등포구,서울특별시:동작구,서울특별시:관악구
HOSPITAL_STATUS_SYNC_TARGET_DELAY_SECONDS=3
```

- [ ] **Step 4: Run deployment tests and verify GREEN**

```powershell
poetry run python -m unittest tests.test_production_sync_worker -v
```

Expected: all deployment tests pass.

- [ ] **Step 5: Confirm Compose is unchanged**

```powershell
git diff --exit-code HEAD -- docker-compose.prod.yml
```

Expected: exit code 0.

### Task 5: Validate the complete implementation

**Files:**
- Verify: `scripts/sync_hospital_status.py`
- Verify: `tests/test_sync_hospital_status.py`
- Verify: `.env.production.example`
- Verify: `tests/test_production_sync_worker.py`

- [ ] **Step 1: Run focused tests**

```powershell
poetry run python -m unittest tests.test_sync_hospital_status tests.test_production_sync_worker -v
```

Expected: all focused tests pass.

- [ ] **Step 2: Run the full test suite**

```powershell
$env:ERMCT_SERVICE_KEY='test-only'; $env:TMAP_APP_KEY='test-only'; poetry run python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 3: Compile all Python sources**

```powershell
poetry run python -m compileall -q app scripts tests
```

Expected: exit code 0 with no output.

- [ ] **Step 4: Review scope and whitespace**

```powershell
git diff --check
git status --short
git diff -- scripts/sync_hospital_status.py tests/test_sync_hospital_status.py .env.production.example tests/test_production_sync_worker.py
```

Expected: no whitespace errors; implementation changes are limited to the four approved files, with the already committed spec and plan documents separate.
