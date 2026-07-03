# KTAS Detail Embedding Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a deterministic, batched OpenAI embedding index from only the KTAS routing index's detail records.

**Architecture:** A standalone script validates and sorts `detail_index`, passes only each detail's `routing_text` to a client-injected batch embedding function, validates/reorders API responses, and joins vectors back to preserved metadata. A thin CLI handles paths, API-key validation, client construction, atomic-after-success output, and clear errors without modifying the existing routing builder or RAG runtime.

**Tech Stack:** Python 3.11, OpenAI Python SDK, `argparse`, `json`, `pathlib`, `unittest`, Poetry

---

## File Structure

- Create `scripts/build_ktas_detail_embedding_index.py`: schema validation, deterministic sorting, batched embedding, output assembly, CLI.
- Create `tests/test_build_ktas_detail_embedding_index.py`: stub-client unit tests and injected CLI tests without network calls.
- Modify `.gitignore`: ignore only `/data/ktas_detail_embedding_index.json` in addition to existing entries.

### Task 1: Load and validate detail records

**Files:**
- Create: `tests/test_build_ktas_detail_embedding_index.py`
- Create: `scripts/build_ktas_detail_embedding_index.py`

- [ ] **Step 1: Write failing input tests**

Create temporary routing JSON containing `category_index`, `complaint_index`, and two intentionally unsorted `detail_index` records. Import `load_detail_items` and assert it returns only detail records sorted by `(detail_key, row_code)`. Add cases for a missing `detail_index`, non-array value, missing metadata, and blank `routing_text`, each asserting a `ValueError` that names the field.

```python
def test_loads_only_sorted_detail_index(self) -> None:
    payload = {
        "category_index": [{"routing_text": "DO NOT EMBED CATEGORY"}],
        "complaint_index": [{"routing_text": "DO NOT EMBED COMPLAINT"}],
        "detail_index": [self.detail("P:B:AD", "CPBAD", "shock text"),
                         self.detail("O:F:AA", "COFAA", "breathing text")],
    }
    items = load_detail_items(self.write_json(payload))
    self.assertEqual(["COFAA", "CPBAD"], [item["row_code"] for item in items])
```

- [ ] **Step 2: Run input tests and verify RED**

Run: `poetry run python -m unittest tests.test_build_ktas_detail_embedding_index.LoadDetailItemsTests -v`

Expected: import failure because the new script does not exist.

- [ ] **Step 3: Implement strict detail loading**

Define `REQUIRED_FIELDS` for all output metadata plus `routing_text`. Implement:

```python
def load_detail_items(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("routing index root must be an object")
    details = payload.get("detail_index")
    if not isinstance(details, list):
        raise ValueError("detail_index must be an array")
    validated = [validate_detail(item, index) for index, item in enumerate(details)]
    return sorted(validated, key=lambda item: (item["detail_key"], item["row_code"]))
```

`validate_detail` requires a JSON object, all fields, integer `ktas`, and non-empty string `routing_text`. Copy only required fields so no root or unrelated detail data leaks into output.

- [ ] **Step 4: Run input tests and verify GREEN**

Run: `poetry run python -m unittest tests.test_build_ktas_detail_embedding_index.LoadDetailItemsTests -v`

Expected: all loading and validation tests pass.

- [ ] **Step 5: Commit input behavior**

```powershell
git add scripts/build_ktas_detail_embedding_index.py tests/test_build_ktas_detail_embedding_index.py
git commit -m "feat: validate KTAS detail embedding inputs"
```

### Task 2: Batch embedding and output assembly

**Files:**
- Modify: `tests/test_build_ktas_detail_embedding_index.py`
- Modify: `scripts/build_ktas_detail_embedding_index.py`

- [ ] **Step 1: Write failing batch-builder tests**

Create a stub client whose `embeddings.create(model, input)` records calls and returns `SimpleNamespace(data=[SimpleNamespace(index=..., embedding=...)])`. Use three details with `batch_size=2`. Assert:

```python
self.assertEqual(
    [["breathing text", "pain text"], ["shock text"]],
    stub.embeddings.inputs,
)
self.assertEqual("text-embedding-3-large", result["embedding_model"])
self.assertEqual("COFAA", result["items"][0]["row_code"])
self.assertEqual("O:F:AA", result["items"][0]["detail_key"])
self.assertEqual("환경손상 > 저체온증 > 중증 호흡곤란",
                 result["items"][0]["canonical_path"])
self.assertEqual(1, result["items"][0]["ktas"])
self.assertEqual([0.1, 0.2], result["items"][0]["embedding"])
self.assertEqual(result["stats"]["detail_row_count"],
                 result["stats"]["embedding_count"])
```

Return response entries in reverse index order and assert they are restored correctly. Add failures for missing, duplicate, out-of-range indexes, non-numeric/non-finite vectors, API exception, and non-positive batch size.

- [ ] **Step 2: Run builder tests and verify RED**

Run: `poetry run python -m unittest tests.test_build_ktas_detail_embedding_index.BuildEmbeddingIndexTests -v`

Expected: import failure for missing `build_embedding_index`.

- [ ] **Step 3: Implement batched embedding**

Define `EmbeddingBuildError(RuntimeError)` and:

```python
def build_embedding_index(
    details: list[dict[str, Any]],
    client: Any,
    model: str,
    batch_size: int,
    source_index: str,
) -> dict[str, Any]:
```

Reject non-positive batch size. Iterate `range(0, len(details), batch_size)`, call `client.embeddings.create(model=model, input=texts)`, and wrap exceptions as `EmbeddingBuildError("embedding API request failed: <type>: <message>")`. Validate response indexes form exactly `range(len(batch))`, sort by index, validate every vector is a non-empty list of finite `int`/`float` values excluding booleans, and append metadata plus the corresponding vector.

Return exactly:

```python
{
    "version": "ktas-detail-embedding-v1",
    "embedding_model": model,
    "source_index": source_index,
    "stats": {"detail_row_count": len(details), "embedding_count": len(items)},
    "items": items,
}
```

- [ ] **Step 4: Run builder tests and verify GREEN**

Run: `poetry run python -m unittest tests.test_build_ktas_detail_embedding_index.BuildEmbeddingIndexTests -v`

Expected: batching, exact text inputs, metadata, counts, response ordering, and clear failures pass.

- [ ] **Step 5: Commit embedding builder**

```powershell
git add scripts/build_ktas_detail_embedding_index.py tests/test_build_ktas_detail_embedding_index.py
git commit -m "feat: batch KTAS detail embeddings"
```

### Task 3: CLI, deterministic output, and ignore policy

**Files:**
- Modify: `tests/test_build_ktas_detail_embedding_index.py`
- Modify: `scripts/build_ktas_detail_embedding_index.py`
- Modify: `.gitignore`

- [ ] **Step 1: Write failing CLI tests**

Call `main(argv, client_factory=stub_factory, environ={"OPENAI_API_KEY": "test-key"})` directly so the full CLI path is exercised without network calls. Use temporary input/output paths and assert return code zero, output creation, requested model/batch size forwarding, and identical output bytes across two runs. Assert the output contains no category/complaint embeddings and its items remain sorted.

Add cases asserting missing `OPENAI_API_KEY`, missing input, API failure, and invalid `--batch-size` return non-zero, print clear stderr messages, and do not create output.

- [ ] **Step 2: Run CLI tests and verify RED**

Run: `poetry run python -m unittest tests.test_build_ktas_detail_embedding_index.CliTests -v`

Expected: failure because `main` and argument parsing are missing.

- [ ] **Step 3: Implement CLI and deterministic serialization**

Add defaults:

```python
--input data/ktas_routing_index.json
--output data/ktas_detail_embedding_index.json
--model text-embedding-3-large
--batch-size 100
```

`main` accepts injectable `client_factory` and `environ` for testing. It validates the input and API key before constructing `OpenAI(api_key=...)`. It catches `OSError`, `json.JSONDecodeError`, `ValueError`, and `EmbeddingBuildError`, prints `error: <message>` to stderr, and returns 1. Build all data before writing:

```python
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
```

On success print the output path, detail row count, and embedding count.

- [ ] **Step 4: Add generated output to `.gitignore`**

Append:

```gitignore
/data/ktas_detail_embedding_index.json
```

- [ ] **Step 5: Run CLI and all focused tests**

Run: `poetry run python -m unittest tests.test_build_ktas_detail_embedding_index -v`

Expected: all focused tests pass without network access.

- [ ] **Step 6: Commit CLI and ignore policy**

```powershell
git add scripts/build_ktas_detail_embedding_index.py tests/test_build_ktas_detail_embedding_index.py .gitignore
git commit -m "feat: add KTAS detail embedding index CLI"
```

### Task 4: Final regression verification

**Files:**
- Verify: `scripts/build_ktas_detail_embedding_index.py`
- Verify: `tests/test_build_ktas_detail_embedding_index.py`
- Verify: `.gitignore`

- [ ] **Step 1: Run focused tests**

Run: `poetry run python -m unittest tests.test_build_ktas_detail_embedding_index -v`

Expected: all focused tests pass.

- [ ] **Step 2: Compile changed and required backend Python**

Run:

```powershell
poetry run python -m py_compile scripts/build_ktas_detail_embedding_index.py app/main.py app/schemas.py app/procedure_groups.py app/services/ermct_client.py app/ktas_engine.py app/stt_cleaner.py
```

Expected: exit code zero with no output.

- [ ] **Step 3: Run backend regression tests**

Run: `poetry run python -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 4: Verify generated-file policy**

Run: `git check-ignore data/ktas_detail_embedding_index.json`

Expected: prints `data/ktas_detail_embedding_index.json`.

- [ ] **Step 5: Confirm repository scope**

Run: `git status --short`

Expected: only pre-existing user changes appear; no generated detail embedding index appears. Existing routing builder and RAG runtime have no diff.
