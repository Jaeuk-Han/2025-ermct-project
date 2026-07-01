# RAG Nonurgent Merge Policy Design

## Scope

Change only the valid-RAG merge branch in `app/ktas_engine.py`. Keep parser, aliases, response schema, fallback contracts, hospital routing, frontend, and deployment configuration unchanged.

## Policy

Confidence below 0.6 or empty evidence continues to select the rule baseline. Parse and validation failures retain the existing rule-based fallback contract.

For a valid, sufficiently supported RAG result:

- RAG 1–3: select `min(rule_based, rag_based)`.
- RAG 4–5 with rule 3: allow the RAG result, with `safety_merge_applied=False` and no fallback reason.
- RAG 4–5 with rule 1–2: preserve the rule result as a strong safety signal, with `safety_merge_applied=True` and `fallback_reason="rule_based_safety_priority"`.

Existing optional metadata remains unchanged and records both source levels and the selected result.

## Testing

Update engine unit tests for rule/RAG combinations across the 1–5 boundary and retain regression coverage for low confidence, empty evidence, parsing failure, and validation failure. Validation uses Poetry compileall, full unittest discovery, and `git diff --check`.
