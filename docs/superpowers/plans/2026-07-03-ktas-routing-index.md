# KTAS Three-Stage Routing Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a validated, deterministic category → complaint → detail JSON routing index from the existing KTAS CSV.

**Architecture:** A standalone standard-library builder parses and validates the fixed eight-column CSV, joins two small JSON enrichment maps, and derives all tree, routing, criterion, collision, schema, and statistics views from one normalized row list. Pure functions are tested directly; a thin CLI resolves paths, writes UTF-8 JSON, and reports warnings and counts.

**Tech Stack:** Python 3.11, `csv`, `json`, `argparse`, `pathlib`, `unittest`, Poetry

---

## File Structure

- Create `scripts/build_ktas_routing_index.py`: parsing, validation, index construction, deterministic serialization, CLI.
- Create `tests/test_build_ktas_routing_index.py`: pure-function and subprocess CLI behavior.
- Create `data/complaint_aliases.json`: complaint-level canonical terms and aliases keyed by complaint key.
- Create `data/detail_feature_hints.json`: detail-level clinical phrases keyed by code and label.
- Modify `.gitignore`: exclude only `data/ktas_routing_index.json`.

### Task 1: CSV parsing and validation

**Files:**
- Create: `tests/test_build_ktas_routing_index.py`
- Create: `scripts/build_ktas_routing_index.py`

- [ ] **Step 1: Write failing parser tests**

Create tests using temporary UTF-8 CSV files. Assert that quoted commas survive, KTAS becomes `int`, invalid KTAS and missing fields are skipped with warnings, and the first duplicate row code/detail key wins. A duplicate record emits both warnings when both identifiers collide.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.build_ktas_routing_index import parse_rows


class ParseRowsTests(unittest.TestCase):
    def write_csv(self, directory: str, content: str) -> Path:
        path = Path(directory) / "input.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def test_parses_quoted_comma_and_integer_ktas(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.write_csv(
                directory,
                'COFAA,O,환경손상,F,저체온증,AA,"중증, 호흡곤란",1\n',
            )
            rows, warnings = parse_rows(path)
        self.assertEqual([], warnings)
        self.assertEqual("중증, 호흡곤란", rows[0]["detail_label"])
        self.assertEqual(1, rows[0]["ktas"])

    def test_skips_invalid_rows_and_keeps_first_duplicate(self) -> None:
        with TemporaryDirectory() as directory:
            path = self.write_csv(
                directory,
                "0,1,2,3,4,5,6,7\n"
                "COFAA,O,환경손상,F,저체온증,AA,중증 호흡곤란,1\n"
                "COFAA,O,환경손상,F,저체온증,AB,경증,4\n"
                "BAD,O,환경손상,F,저체온증,AC,기준,not-int\n"
                ",O,환경손상,F,저체온증,AD,기준,2\n",
            )
            rows, warnings = parse_rows(path)
        self.assertEqual(["COFAA"], [row["row_code"] for row in rows])
        self.assertTrue(any("duplicate row_code=COFAA" in item for item in warnings))
        self.assertTrue(any("duplicate detail_key=O:F:AA" in item for item in warnings))
        self.assertTrue(any("invalid ktas" in item for item in warnings))
        self.assertTrue(any("missing required fields" in item for item in warnings))
```

- [ ] **Step 2: Run tests and verify RED**

Run: `poetry run python -m unittest tests.test_build_ktas_routing_index.ParseRowsTests -v`

Expected: import failure because `scripts.build_ktas_routing_index` does not exist.

- [ ] **Step 3: Implement the minimal parser**

Define `FIELD_NAMES`, a `RoutingRow` typed dictionary, and:

```python
def parse_rows(path: Path) -> tuple[list[RoutingRow], list[str]]:
    rows: list[RoutingRow] = []
    warnings: list[str] = []
    seen_row_codes: set[str] = set()
    seen_detail_keys: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_number, raw in enumerate(csv.reader(handle), start=1):
            if not raw or all(not cell.strip() for cell in raw):
                continue
            values = (raw + [""] * len(FIELD_NAMES))[: len(FIELD_NAMES)]
            record = dict(zip(FIELD_NAMES, (cell.strip() for cell in values)))
            missing = [name for name in FIELD_NAMES[:-1] if not record[name]]
            if missing:
                warnings.append(
                    f"line {line_number}: missing required fields: {', '.join(missing)}"
                )
                continue
            try:
                ktas = int(record["ktas"])
            except ValueError:
                warnings.append(f"line {line_number}: invalid ktas={record['ktas']!r}")
                continue
            row_code = record["row_code"]
            parsed_detail_key = (
                f"{record['category_code']}:{record['complaint_code']}:{record['detail_code']}"
            )
            duplicate = False
            if row_code in seen_row_codes:
                warnings.append(f"line {line_number}: duplicate row_code={row_code}")
                duplicate = True
            if parsed_detail_key in seen_detail_keys:
                warnings.append(
                    f"line {line_number}: duplicate detail_key={parsed_detail_key}"
                )
                duplicate = True
            if duplicate:
                continue
            seen_row_codes.add(row_code)
            seen_detail_keys.add(parsed_detail_key)
            rows.append({**record, "ktas": ktas})
    return rows, warnings
```

Keep the eight fields in this exact order: `row_code`, `category_code`, `category_label`, `complaint_code`, `complaint_label`, `detail_code`, `detail_label`, `ktas`.

- [ ] **Step 4: Run parser tests and verify GREEN**

Run: `poetry run python -m unittest tests.test_build_ktas_routing_index.ParseRowsTests -v`

Expected: both tests pass.

- [ ] **Step 5: Commit parser behavior**

```powershell
git add scripts/build_ktas_routing_index.py tests/test_build_ktas_routing_index.py
git commit -m "feat: parse KTAS routing source rows"
```

### Task 2: Auxiliary data validation and routing indexes

**Files:**
- Modify: `tests/test_build_ktas_routing_index.py`
- Modify: `scripts/build_ktas_routing_index.py`
- Create: `data/complaint_aliases.json`
- Create: `data/detail_feature_hints.json`

- [ ] **Step 1: Write failing index-construction tests**

Add a three-row fixture with two categories sharing one complaint label and two complaint paths sharing one detail label. Call `build_index(rows, aliases, hints)` and assert:

```python
self.assertEqual("O:F", result["complaint_index"][0]["complaint_key"])
self.assertEqual("O:F:AA", result["detail_index"][0]["detail_key"])
self.assertNotIn("중증 호흡곤란", result["category_index"][0]["routing_text"])
self.assertNotIn("중증 호흡곤란", result["complaint_index"][0]["routing_text"])
self.assertNotIn("KTAS", result["detail_index"][0]["routing_text"])
self.assertIn("SpO2 저하", result["detail_index"][0]["routing_text"])
self.assertIn("저체온", result["complaint_index"][0]["routing_text"])
self.assertEqual(2, len(result["complaint_label_collision_index"]["저체온증"]))
self.assertEqual(2, len(result["detail_label_collision_index"]["중증 호흡곤란"]))
self.assertIn("AA|중증 호흡곤란|1", result["criterion_index"])
```

Also assert that categories contain complaints and complaints contain detail records, `canonical_path` uses ` > `, and stats equal the fixture counts.

Assert every criterion and collision entry exposes `row_code` as its evidence identifier. `detail_key` remains a routing/grouping identifier and never replaces `row_code` in evidence records. Build fixtures with surrounding whitespace in repeated labels and assert collision keys and paths use stripped labels.

- [ ] **Step 2: Run index tests and verify RED**

Run: `poetry run python -m unittest tests.test_build_ktas_routing_index.BuildIndexTests -v`

Expected: import failure for missing `build_index`.

- [ ] **Step 3: Implement normalized index construction**

Add helpers:

```python
def complaint_key(row: RoutingRow) -> str:
    return f"{row['category_code']}:{row['complaint_code']}"


def detail_key(row: RoutingRow) -> str:
    return f"{complaint_key(row)}:{row['detail_code']}"


def join_text(parts: Iterable[str]) -> str:
    return " ".join(dict.fromkeys(part.strip() for part in parts if part.strip()))
```

Implement `build_index(rows, aliases, feature_hints)` from sorted rows. Build one detail record per retained CSV row. Deduplicate category and complaint records by code-derived keys. Use `detail_code|detail_label` for hint lookup. Build collision dictionaries only when a label maps to more than one key. Group criteria under `detail_code|detail_label|ktas`. Return all root fields required by the design.

The routing text inputs must be exact:

```python
category_text = [category_label, *complaint_labels]
complaint_text = [category_label, complaint_label, *canonical_terms, *aliases]
detail_text = [category_label, complaint_label, detail_label, *feature_hints]
```

- [ ] **Step 4: Add and validate auxiliary JSON loaders**

Implement `load_aliases(path)` and `load_feature_hints(path)` using `json.load`. Require a root object, string keys, string-array alias fields, and string-array hint values. Raise `ValueError` naming the invalid key on shape errors.

Seed tracked JSON with the prompt examples:

```json
{
  "O:F": {
    "canonical_terms": ["저체온증", "hypothermia"],
    "aliases": ["저체온", "몸이 차갑다", "체온이 낮다", "추위에 오래 노출", "hypothermia"]
  },
  "P:B": {
    "canonical_terms": ["쏘임", "sting"],
    "aliases": ["쏘였다", "벌에 쏘임", "곤충에 쏘임", "bee sting", "insect sting"]
  }
}
```

and the four example hint keys `AA|중증 호흡곤란`, `AD|쇼크`, `AG|무의식(U, GCS 3-8)`, and `BG|급성 통증(8-10)` with the phrases supplied in `.codex/codex_prompt.md`.

- [ ] **Step 5: Run index tests and verify GREEN**

Run: `poetry run python -m unittest tests.test_build_ktas_routing_index.BuildIndexTests -v`

Expected: all hierarchy, collision, criterion, enrichment, and routing-boundary tests pass.

- [ ] **Step 6: Commit indexes and enrichment data**

```powershell
git add scripts/build_ktas_routing_index.py tests/test_build_ktas_routing_index.py data/complaint_aliases.json data/detail_feature_hints.json
git commit -m "feat: build three-stage KTAS routing indexes"
```

### Task 3: Deterministic CLI and generated-file policy

**Files:**
- Modify: `tests/test_build_ktas_routing_index.py`
- Modify: `scripts/build_ktas_routing_index.py`
- Modify: `.gitignore`

- [ ] **Step 1: Write a failing CLI test**

Use `subprocess.run` with `sys.executable`, temporary input/output/enrichment files, and the repository script path. Assert exit code zero, output file existence, `stats` values, warning text on stderr for a metadata row, and summary counts on stdout. Run the command twice and assert output bytes are identical. Add separate cases proving omitted `--aliases`/`--feature-hints` use empty maps, while explicitly supplied missing paths exit non-zero with clear messages naming the missing file.

- [ ] **Step 2: Run the CLI test and verify RED**

Run: `poetry run python -m unittest tests.test_build_ktas_routing_index.CliTests -v`

Expected: failure because CLI argument parsing and serialization are missing.

- [ ] **Step 3: Implement CLI and deterministic serialization**

Add required defaults only for `--input` and `--output`. Define `--aliases` and `--feature-hints` with `default=None`; load an empty map when omitted. When either option is explicitly supplied, require that file to exist and fail through `parser.error(...)` with the option name and path. Write with:

```python
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
```

Print each validation warning to `sys.stderr`. Print output path and category, complaint, detail row, and unique criterion counts to stdout.

- [ ] **Step 4: Exclude the generated index only**

Append this repository-relative entry to `.gitignore`:

```gitignore
/data/ktas_routing_index.json
```

- [ ] **Step 5: Run CLI tests and verify GREEN**

Run: `poetry run python -m unittest tests.test_build_ktas_routing_index.CliTests -v`

Expected: CLI test passes and output bytes match across builds.

- [ ] **Step 6: Commit CLI and ignore policy**

```powershell
git add scripts/build_ktas_routing_index.py tests/test_build_ktas_routing_index.py .gitignore
git commit -m "feat: add deterministic KTAS routing index CLI"
```

### Task 4: Real-data build and regression verification

**Files:**
- Verify: `scripts/build_ktas_routing_index.py`
- Verify: `data/original_pre-ktas.csv`
- Generated, ignored: `data/ktas_routing_index.json`

- [ ] **Step 1: Run all focused tests**

Run: `poetry run python -m unittest tests.test_build_ktas_routing_index -v`

Expected: all focused tests pass.

- [ ] **Step 2: Build from the real CSV**

Run:

```powershell
poetry run python scripts/build_ktas_routing_index.py --input data/original_pre-ktas.csv --output data/ktas_routing_index.json --aliases data/complaint_aliases.json --feature-hints data/detail_feature_hints.json
```

Expected: successful exit, warnings for the two leading metadata rows, non-zero category/complaint/detail/criterion statistics, and a UTF-8 JSON output file.

- [ ] **Step 3: Verify required root fields and Git exclusion**

Run:

```powershell
poetry run python -c "import json; from pathlib import Path; p=Path('data/ktas_routing_index.json'); d=json.loads(p.read_text(encoding='utf-8')); required={'version','schema','stats','categories','category_index','complaint_index','detail_index','criterion_index','complaint_label_collision_index','detail_label_collision_index'}; assert required <= d.keys(); assert all(d['stats'][k] > 0 for k in ('category_count','complaint_count','detail_row_count','unique_criterion_count')); print(d['stats'])"
git check-ignore data/ktas_routing_index.json
```

Expected: statistics print, assertions do not fail, and `git check-ignore` prints the generated path.

- [ ] **Step 4: Run backend regression tests**

Run: `poetry run python -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 5: Compile changed Python**

Run: `poetry run python -m py_compile scripts/build_ktas_routing_index.py`

Expected: exit code zero with no output.

- [ ] **Step 6: Confirm repository scope**

Run: `git status --short`

Expected: `data/ktas_routing_index.json` is absent; unrelated pre-existing user changes remain untouched.
