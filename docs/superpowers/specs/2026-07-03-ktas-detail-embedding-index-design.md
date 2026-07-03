# KTAS Detail Embedding Index Design

## Goal

Build a standalone embedding index from only the `detail_index` records in `data/ktas_routing_index.json`. The result supports a later hierarchical RAG stage that compares a patient utterance only with detail rows belonging to an already selected category and complaint.

## Scope

- Add `scripts/build_ktas_detail_embedding_index.py`.
- Add `tests/test_build_ktas_detail_embedding_index.py`.
- Ignore `/data/ktas_detail_embedding_index.json`.
- Do not modify `scripts/build_ktas_routing_index.py`.
- Do not connect the generated index to the existing RAG runtime.
- Do not embed `category_index` or `complaint_index`.

## Architecture

The script has three boundaries:

1. Input validation loads the routing index and extracts only `detail_index`.
2. A client-injected builder deterministically sorts details, embeds their `routing_text` values in batches, validates the responses, and joins embeddings back to metadata.
3. The CLI validates configuration, creates the OpenAI client, writes deterministic JSON, and converts configuration or API failures into clear non-zero errors.

OpenAI access remains at the CLI boundary. Unit tests pass a stub client and never make network calls.

## Input Validation

The input must be a JSON object containing a `detail_index` array. Each detail item must contain:

- `row_code`
- `detail_key`
- `category_code`
- `category_label`
- `complaint_code`
- `complaint_label`
- `detail_code`
- `detail_label`
- `canonical_path`
- `ktas`
- non-empty `routing_text`

Other root indexes are ignored. Missing or malformed required fields fail before any API call and identify the failing item and field.

## Deterministic Ordering

Details are sorted by `detail_key`, then `row_code`. This order controls embedding inputs and final `items`. JSON is written as UTF-8 with indentation, `ensure_ascii=False`, and sorted object keys. Given the same source and embedding responses, output bytes are identical.

## Batch Embedding

The default model is `text-embedding-3-large`, matching the existing RAG configuration. The default batch size is 100 and can be overridden with `--batch-size` using a positive integer.

For each batch, the script calls:

```python
client.embeddings.create(model=model, input=routing_texts)
```

Response entries are ordered by their response `index`, not assumed to arrive in list order. Every batch must return exactly one finite numeric vector per input index, with no missing or duplicate indexes. Any mismatch fails the build; partial output is not written.

## Output

The root object contains:

- `version`: `ktas-detail-embedding-v1`
- `embedding_model`: selected model
- `source_index`: the CLI input path serialized with forward slashes
- `stats.detail_row_count`
- `stats.embedding_count`
- `items`

Each output item preserves the requested detail metadata and `routing_text`, then adds `embedding`. `row_code` remains the evidence identifier; `detail_key` remains the hierarchical routing identifier.

## Error Handling

- A missing input file produces a CLI parser error naming the path.
- Missing `OPENAI_API_KEY` fails before constructing the client and names the variable.
- Invalid `--batch-size` produces a CLI parser error.
- Input schema failures produce a concise validation error.
- OpenAI failures are wrapped as `embedding API request failed: <error type>: <message>` and exit non-zero.
- Output is written only after every batch and count validation succeeds.

Secrets are never printed. The API key is used only to construct the client.

## CLI

```powershell
poetry run python scripts/build_ktas_detail_embedding_index.py --input data/ktas_routing_index.json --output data/ktas_detail_embedding_index.json --model text-embedding-3-large
```

`--input`, `--output`, and `--model` have the values above as defaults. `--batch-size` defaults to 100.

## Testing

Tests use `unittest`, temporary files, and a local stub embedding client. They verify:

- only `detail_index` supplies embedding inputs;
- metadata and `row_code` evidence are preserved;
- exact `routing_text` values reach the client;
- batch calls and response-index reordering work;
- embedding count equals detail row count;
- output order and bytes are deterministic;
- CLI creates the requested output without real OpenAI calls;
- missing API key and API failures return clear errors;
- malformed or mismatched embedding responses fail without output.

## Repository Policy

`data/ktas_detail_embedding_index.json` is generated, costly to reproduce, and potentially large. It is excluded through `.gitignore` and is not committed. Source code and tests are tracked.
