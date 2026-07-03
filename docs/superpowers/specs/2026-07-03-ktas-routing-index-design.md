# KTAS Three-Stage Routing Index Design

## Goal

Transform `data/original_pre-ktas.csv` into a deterministic JSON index that routes a patient utterance through category, complaint, and detail stages without comparing the utterance against every KTAS detail row.

## Scope

- Add `scripts/build_ktas_routing_index.py`.
- Add complaint aliases keyed by `category_code:complaint_code`.
- Add detail feature hints keyed by `detail_code|detail_label`.
- Generate `data/ktas_routing_index.json` locally and exclude it from Git.
- Add focused unit and CLI tests for parsing, validation, hierarchy, collisions, routing text, and output generation.
- Do not change the source CSV, current KTAS runtime classifier, or existing RAG index builder.

## Input Parsing

The builder uses `csv.reader` with UTF-8 and `newline=""`, preserving quoted commas in labels. Rows are interpreted by their fixed eight-column order:

1. `row_code`
2. `category_code`
3. `category_label`
4. `complaint_code`
5. `complaint_label`
6. `detail_code`
7. `detail_label`
8. `ktas`

The current CSV begins with two metadata rows rather than the documented field names. The parser treats any non-empty row as data, validates all required fields and integer KTAS, emits a warning for invalid rows, and skips them. It never modifies the source CSV. Duplicate `row_code` values emit warnings; the first valid row is retained so output remains deterministic.

## Auxiliary Data

`data/complaint_aliases.json` is an object keyed by `complaint_key`, formatted as `{category_code}:{complaint_code}`. Each value may contain `canonical_terms` and `aliases` arrays. Missing keys produce empty arrays.

`data/detail_feature_hints.json` is an object keyed by `{detail_code}|{detail_label}`. Each value is an array of detail-level clinical phrases. Missing keys produce an empty array.

Malformed auxiliary JSON or values with the wrong shape fail the build with a clear error rather than silently producing an incomplete index.

## Output Model

The root JSON contains:

- `version`: schema version `1`.
- `schema`: descriptions of stable key formats and source columns.
- `stats`: category, complaint, detail-row, and unique-criterion counts.
- `categories`: category → complaint → details hierarchy.
- `category_index`: stage-one routing records.
- `complaint_index`: stage-two routing records.
- `detail_index`: stage-three embedding candidates.
- `criterion_index`: details grouped by `detail_code|detail_label|ktas`.
- `complaint_label_collision_index`: repeated complaint labels across categories.
- `detail_label_collision_index`: repeated detail labels across complaint paths.

All lists are sorted by source code keys and JSON object keys are emitted consistently. Running the builder twice with identical inputs produces identical content.

## Routing Records

### Category stage

Each category record contains its code, label, complaint count, and `routing_text`. The text contains only the category label and complaint labels. It never contains detail labels, aliases, feature hints, or KTAS grades.

### Complaint stage

Each complaint record contains `complaint_key`, category and complaint fields, `canonical_path`, canonical terms, aliases, detail count, and `routing_text`. The text contains category label, complaint label, canonical terms, and aliases. It never contains detail labels, feature hints, or KTAS grades.

### Detail stage

Each detail record contains `detail_key`, `row_code`, category, complaint, and detail fields, `canonical_path`, integer `ktas`, feature hints, and `routing_text`. The text contains category label, complaint label, detail label, and feature hints. KTAS grade remains metadata and is not embedded in `routing_text`.

`complaint_key` is `{category_code}:{complaint_code}`. `detail_key` is `{category_code}:{complaint_code}:{detail_code}`. Evidence consumers should use `row_code` as the primary source identifier.

## Collision and Criterion Indexes

Complaint labels are not globally unique. `complaint_label_collision_index` includes only labels mapped to more than one complaint key and stores each matching `complaint_key` and `canonical_path`.

Detail labels are not globally unique. `detail_label_collision_index` includes only labels mapped to more than one detail key and stores each matching `detail_key`, `row_code`, and `canonical_path`.

`criterion_index` is keyed by `{detail_code}|{detail_label}|{ktas}` because detail codes and labels can repeat independently. Each entry stores matching `detail_key`, `row_code`, and `canonical_path` records.

## CLI

The supported command is:

```powershell
poetry run python scripts/build_ktas_routing_index.py --input data/original_pre-ktas.csv --output data/ktas_routing_index.json --aliases data/complaint_aliases.json --feature-hints data/detail_feature_hints.json
```

Warnings are written to standard error. A successful build prints the output path and all four statistics. The parent output directory is created when necessary.

## Testing

Tests use `unittest` through Poetry and temporary files. Coverage includes quoted commas, invalid KTAS, missing required fields, duplicate row codes, hierarchy construction, routing-text stage boundaries, alias/hint lookup keys, criterion grouping, label collision indexes, deterministic output, and CLI generation. Full backend unit tests and Python compilation run after focused tests pass.

## Repository Policy

`data/ktas_routing_index.json` is reproducible and potentially large, so it is added to `.gitignore` and not committed. The builder, auxiliary source JSON files, tests, design, and implementation plan are tracked.
