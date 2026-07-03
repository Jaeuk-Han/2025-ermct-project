# KTAS Detail Embedding Store Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an immutable runtime store that validates a KTAS detail embedding index and ranks candidates only inside a selected category/complaint group.

**Architecture:** `KtasDetailEmbeddingStore.load()` converts validated JSON items into frozen records and a read-only `(category_code, complaint_code)` group map. `search()` validates an externally supplied vector, computes cosine similarity without API calls, and returns deterministically ranked evidence dictionaries.

**Tech Stack:** Python 3.11 standard library, `dataclasses`, `types.MappingProxyType`, `json`, `math`, `unittest`, Poetry

---

## File Structure

- Create `app/ktas_detail_embedding_store.py`: frozen item model, index validation, immutable grouping, cosine search.
- Create `tests/test_ktas_detail_embedding_store.py`: temporary JSON fixtures covering load and search behavior.
- Do not modify engine, RAG runtime, routing builder, or embedding builder.

### Task 1: Validated immutable index loading

**Files:**
- Create: `tests/test_ktas_detail_embedding_store.py`
- Create: `app/ktas_detail_embedding_store.py`

- [ ] **Step 1: Write failing valid-load and root-validation tests**

Create a fixture helper that writes a small index to `TemporaryDirectory`. Test a valid two-item load and assert `embedding_dimension`, item count, and group keys. Add failures for wrong version and `stats.detail_row_count != len(items)`.

```python
def test_loads_valid_index_and_builds_groups(self) -> None:
    store = KtasDetailEmbeddingStore.load(self.write_index([
        self.item("CHAAA", "H:A:AA", "H", "A", [1.0, 0.0]),
        self.item("CHBAA", "H:B:AA", "H", "B", [0.0, 1.0]),
    ]))
    self.assertEqual(2, store.embedding_dimension)
    self.assertEqual({("H", "A"), ("H", "B")}, set(store.group_keys))
```

- [ ] **Step 2: Run load tests and verify RED**

Run: `poetry run python -m unittest tests.test_ktas_detail_embedding_store.LoadStoreTests -v`

Expected: import failure because `app.ktas_detail_embedding_store` does not exist.

- [ ] **Step 3: Implement root validation and frozen records**

Add:

```python
@dataclass(frozen=True)
class DetailEmbeddingItem:
    row_code: str
    detail_key: str
    category_code: str
    category_label: str
    complaint_code: str
    complaint_label: str
    detail_code: str
    detail_label: str
    canonical_path: str
    ktas: int
    routing_text: str
    embedding: tuple[float, ...]
```

Implement `KtasDetailEmbeddingStore.load(path)` to validate the root object, exact version, integer count excluding booleans, array items, and count equality. Convert records to tuples and group with `defaultdict(list)`, then freeze each list as a tuple and the outer map with `MappingProxyType`.

- [ ] **Step 4: Run load tests and verify GREEN**

Run: `poetry run python -m unittest tests.test_ktas_detail_embedding_store.LoadStoreTests -v`

Expected: valid load, version rejection, and count mismatch tests pass.

- [ ] **Step 5: Commit root loading**

```powershell
git add app/ktas_detail_embedding_store.py tests/test_ktas_detail_embedding_store.py
git commit -m "feat: load KTAS detail embedding store"
```

### Task 2: Item and vector validation

**Files:**
- Modify: `tests/test_ktas_detail_embedding_store.py`
- Modify: `app/ktas_detail_embedding_store.py`

- [ ] **Step 1: Write failing item-validation tests**

For each required string field, remove it and assert the error contains `items[0].<field>`. Add cases for boolean/non-integer KTAS, empty embedding, `NaN`, infinity, booleans inside vectors, and inconsistent dimensions.

```python
def test_rejects_inconsistent_embedding_dimensions(self) -> None:
    with self.assertRaisesRegex(ValueError, "embedding dimension"):
        KtasDetailEmbeddingStore.load(self.write_index([
            self.item("CHAAA", "H:A:AA", "H", "A", [1.0, 0.0]),
            self.item("CHAAB", "H:A:AB", "H", "A", [1.0]),
        ]))
```

- [ ] **Step 2: Run item tests and verify RED**

Run: `poetry run python -m unittest tests.test_ktas_detail_embedding_store.ItemValidationTests -v`

Expected: failures because item validation is incomplete.

- [ ] **Step 3: Implement complete item validation**

Create `_parse_item(raw, index, expected_dimension)` that requires all ten string fields to be non-empty, KTAS to be an integer excluding bool, and embedding to be a non-empty list of finite numeric values excluding bool. Convert numbers to floats and reject dimensions differing from the first item with expected/actual values.

- [ ] **Step 4: Run all loading tests and verify GREEN**

Run: `poetry run python -m unittest tests.test_ktas_detail_embedding_store.LoadStoreTests tests.test_ktas_detail_embedding_store.ItemValidationTests -v`

Expected: all root, metadata, vector, and dimension tests pass.

- [ ] **Step 5: Commit complete validation**

```powershell
git add app/ktas_detail_embedding_store.py tests/test_ktas_detail_embedding_store.py
git commit -m "feat: validate KTAS detail embeddings"
```

### Task 3: Filtered cosine search and deterministic ranking

**Files:**
- Modify: `tests/test_ktas_detail_embedding_store.py`
- Modify: `app/ktas_detail_embedding_store.py`

- [ ] **Step 1: Write failing search-validation tests**

Assert `top_k` rejects zero, negative, boolean, and non-integer values. Assert empty, non-finite, boolean-containing, and wrong-dimension query vectors fail before group lookup. Assert a valid query for a missing group returns `[]`.

- [ ] **Step 2: Write failing ranking tests**

Use two complaints under one category and assert only the selected group appears. Use known two-dimensional vectors to assert cosine ranking. Add equal-similarity rows in reverse source order and assert `row_code`, then `detail_key`, ascending tie-break. Add a zero-vector item and assert similarity `0.0`.

```python
self.assertEqual(
    ["CHA01", "CHA02", "CHA03"],
    [result["row_code"] for result in results],
)
self.assertEqual(
    {"row_code", "detail_key", "category_code", "complaint_code",
     "canonical_path", "detail_label", "ktas", "similarity"},
    set(results[0]),
)
```

- [ ] **Step 3: Run search tests and verify RED**

Run: `poetry run python -m unittest tests.test_ktas_detail_embedding_store.SearchTests -v`

Expected: failure because `search()` is missing.

- [ ] **Step 4: Implement query validation and cosine ranking**

Implement:

```python
def search(
    self,
    query_embedding: Sequence[float],
    category_code: str,
    complaint_code: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
```

Validate `top_k` and query before reading the group. Compute cosine using precomputed query norm and item tuples; return `0.0` for either zero norm. Sort with `key=lambda result: (-result["similarity"], result["row_code"], result["detail_key"])` and slice to `top_k`.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `poetry run python -m unittest tests.test_ktas_detail_embedding_store -v`

Expected: all load, validation, filtering, ranking, tie-break, zero-norm, and missing-group tests pass.

- [ ] **Step 6: Commit search behavior**

```powershell
git add app/ktas_detail_embedding_store.py tests/test_ktas_detail_embedding_store.py
git commit -m "feat: search KTAS detail embedding groups"
```

### Task 4: Scope and regression verification

**Files:**
- Verify: `app/ktas_detail_embedding_store.py`
- Verify: `tests/test_ktas_detail_embedding_store.py`

- [ ] **Step 1: Run focused tests**

Run: `poetry run python -m unittest tests.test_ktas_detail_embedding_store -v`

Expected: all focused tests pass.

- [ ] **Step 2: Compile required Python**

Run:

```powershell
poetry run python -m py_compile app/ktas_detail_embedding_store.py app/main.py app/schemas.py app/procedure_groups.py app/services/ermct_client.py app/ktas_engine.py app/stt_cleaner.py
```

Expected: exit code zero with no output.

- [ ] **Step 3: Run backend regression tests**

Run: `poetry run python -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 4: Verify generated index remains ignored**

Run: `git check-ignore data/ktas_detail_embedding_index.json` followed by `git status --short`.

Expected: the generated path is printed by `check-ignore` and absent from status.

- [ ] **Step 5: Verify isolation from existing runtime and builders**

Run:

```powershell
git diff main -- app/ktas_engine.py app/ktas_rag.py scripts/build_ktas_routing_index.py scripts/build_ktas_detail_embedding_index.py
```

Expected: no output.
