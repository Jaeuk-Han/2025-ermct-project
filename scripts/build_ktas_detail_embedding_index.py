from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Callable, Mapping


REQUIRED_FIELDS = (
    "row_code", "detail_key", "category_code", "category_label",
    "complaint_code", "complaint_label", "detail_code", "detail_label",
    "canonical_path", "ktas", "routing_text",
)


class EmbeddingBuildError(RuntimeError):
    pass


def load_detail_items(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("routing index root must be an object")
    details = payload.get("detail_index")
    if not isinstance(details, list):
        raise ValueError("detail_index must be an array")
    validated = []
    for index, item in enumerate(details):
        if not isinstance(item, dict):
            raise ValueError(f"detail_index[{index}] must be an object")
        for field in REQUIRED_FIELDS:
            value = item.get(field)
            if field == "ktas":
                if not isinstance(value, int) or isinstance(value, bool):
                    raise ValueError(f"detail_index[{index}].ktas must be an integer")
            elif not isinstance(value, str) or not value.strip():
                raise ValueError(f"detail_index[{index}].{field} must be a non-empty string")
        validated.append({field: item[field] for field in REQUIRED_FIELDS})
    return sorted(validated, key=lambda item: (item["detail_key"], item["row_code"]))


def build_embedding_index(
    details: list[dict[str, Any]],
    client: Any,
    model: str,
    batch_size: int,
    source_index: str,
) -> dict[str, Any]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    items: list[dict[str, Any]] = []
    for start in range(0, len(details), batch_size):
        batch = details[start : start + batch_size]
        try:
            response = client.embeddings.create(
                model=model, input=[item["routing_text"] for item in batch]
            )
        except Exception as exc:
            raise EmbeddingBuildError(
                f"embedding API request failed: {type(exc).__name__}: {exc}"
            ) from None
        data = list(response.data)
        indexes = [entry.index for entry in data]
        if sorted(indexes) != list(range(len(batch))) or len(set(indexes)) != len(indexes):
            raise EmbeddingBuildError("embedding response indexes do not match batch inputs")
        for entry in sorted(data, key=lambda value: value.index):
            vector = entry.embedding
            if (
                not isinstance(vector, list)
                or not vector
                or not all(
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(value)
                    for value in vector
                )
            ):
                raise EmbeddingBuildError("embedding vector must contain finite numeric values")
            items.append({**batch[entry.index], "embedding": vector})
    return {
        "version": "ktas-detail-embedding-v1",
        "embedding_model": model,
        "source_index": source_index,
        "stats": {
            "detail_row_count": len(details),
            "embedding_count": len(items),
        },
        "items": items,
    }


def main(
    argv: list[str] | None = None,
    *,
    client_factory: Callable[..., Any] | None = None,
    environ: Mapping[str, str] | None = None,
) -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build KTAS detail embedding index.")
    parser.add_argument("--input", type=Path, default=root / "data" / "ktas_routing_index.json")
    parser.add_argument("--output", type=Path, default=root / "data" / "ktas_detail_embedding_index.json")
    parser.add_argument("--model", default="text-embedding-3-large")
    parser.add_argument("--batch-size", type=int, default=100)
    try:
        args = parser.parse_args(argv)
        if args.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        env = os.environ if environ is None else environ
        api_key = env.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        if client_factory is None:
            from openai import OpenAI

            client_factory = OpenAI
        details = load_detail_items(args.input)
        result = build_embedding_index(
            details,
            client_factory(api_key=api_key),
            args.model,
            args.batch_size,
            args.input.as_posix(),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (OSError, json.JSONDecodeError, ValueError, EmbeddingBuildError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"output={args.output}")
    print(f"detail_row_count={result['stats']['detail_row_count']}")
    print(f"embedding_count={result['stats']['embedding_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
