# Nearest Top3 Order Design

## Scope

Fix only the ordering defect in `/api/ktas/route/seoul/nearest`. Do not change candidate filtering, `priority_score`, recommendation scoring, fallback budgets, RAG KTAS, frontend UI, or deployment configuration.

## Data flow

The distance request payload will include each hospital HPID as `id`. `calculate_all_distances_async` will preserve that ID, plus coverage and priority values needed for deterministic tie-breaking, in each successful result. Failed TMAP results remain excluded.

`get_top3` will sort successful results by distance ascending, duration ascending, coverage descending, then priority descending. Missing duration sorts last. The nearest endpoint will index request hospitals by HPID and iterate the sorted `top3_results`, so its response order exactly matches the TMAP ranking and duplicate hospital names cannot collide.

## Compatibility

No response fields or frontend behavior change. Existing distance and duration fields are populated as before. Name-based matching is removed because HPID is already available on every routing candidate.

## Testing

Unit tests cover the Severance regression example, every tie-break level, partial TMAP failures, duplicate hospital names, and proof that original priority order is not restored. Validation uses Poetry compileall, full unittest discovery, and `git diff --check`.
