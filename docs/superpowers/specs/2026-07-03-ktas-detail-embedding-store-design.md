# KTAS Detail Embedding Store Design

## Goal

Provide an independent runtime store that loads the generated KTAS detail embedding index and ranks detail candidates only within a selected `(category_code, complaint_code)` group. This work does not connect hierarchical retrieval to the KTAS engine or existing RAG runtime.

## Public API

```python
store = KtasDetailEmbeddingStore.load(
    Path("data/ktas_detail_embedding_index.json")
)
results = store.search(
    query_embedding=[0.1, 0.2, 0.3],
    category_code="H",
    complaint_code="A",
    top_k=5,
)
```

`load()` validates the complete index before returning. `search()` accepts an already-created query vector and performs no network or OpenAI operation.

## Input Contract

The root JSON must:

- be an object;
- have `version == "ktas-detail-embedding-v1"`;
- contain an object `stats` with a non-negative integer `detail_row_count`;
- contain an `items` array;
- have `stats.detail_row_count == len(items)`.

Each item must be an object containing:

- non-empty strings: `row_code`, `detail_key`, `category_code`, `category_label`, `complaint_code`, `complaint_label`, `detail_code`, `detail_label`, `canonical_path`, `routing_text`;
- integer `ktas` excluding booleans;
- a non-empty embedding array containing finite numeric values excluding booleans.

All embedding vectors must have the same dimension. Validation errors identify the failing root field or item index and field. The loader fails before exposing a partially valid store.

## Immutable Store

Validated items are represented by an internal frozen record. Embeddings are converted to tuples. The group index is constructed once as a mapping from `(category_code, complaint_code)` to tuples of records and exposed internally through a read-only mapping. Search results are new dictionaries, so callers cannot mutate stored records.

The store records the common embedding dimension. An empty index is valid only when `detail_row_count` is zero; its dimension is zero and any search group is empty.

## Search Validation

`search()` requires:

- `top_k` to be an integer greater than zero, excluding booleans;
- query embedding to be a non-empty sequence of finite numeric values, excluding booleans;
- query dimension to equal the store dimension when the store contains items.

Validation occurs before group lookup, so an invalid query does not silently return an empty result merely because the category/complaint group is absent. A valid query for a missing group returns `[]`.

## Ranking

Search scans only the tuple mapped to the requested category and complaint. Similarity is cosine similarity. If either vector has zero norm, similarity is `0.0`.

Results are sorted deterministically by:

1. similarity descending;
2. `row_code` ascending;
3. `detail_key` ascending.

At most `top_k` records are returned. Each result contains `row_code`, `detail_key`, `category_code`, `complaint_code`, `canonical_path`, `detail_label`, `ktas`, and `similarity`. `row_code` remains the evidence identifier.

## Error Model

Malformed index data raises `ValueError` with field context. File-not-found, permission, and malformed JSON errors retain their standard exception types. Invalid search arguments and dimension mismatches raise `ValueError` with expected and actual values where relevant.

## Testing

`tests/test_ktas_detail_embedding_store.py` uses only small JSON fixtures in temporary directories. Tests cover valid loading, version and count validation, missing metadata, invalid vectors, inconsistent dimensions, invalid query vectors, dimension mismatch, invalid `top_k`, exact group filtering, exclusion of other complaints, cosine ranking, deterministic ties, zero norms, and missing groups.

Focused tests, required Python compilation, and the complete backend unit suite must pass. Verification also confirms that the generated embedding index remains ignored and that `app/ktas_engine.py`, `app/ktas_rag.py`, `scripts/build_ktas_routing_index.py`, and `scripts/build_ktas_detail_embedding_index.py` are unchanged.
